import io
import json
import datetime
from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.migration import MigrationJob, MigrationStaging, MigrationError, MigrationStatus, StagingValidationStatus
from app.models.book import Book, BookItem, BookItemStatus
from app.models.member import Member, MemberStatus
from app.services.audit_service import AuditService


class MigrationService:
    @staticmethod
    def upload_and_stage(db: Session, file: UploadFile, file_type: str = "BOOKS") -> MigrationJob:
        content = file.file.read()
        try:
            if file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
                df = pd.read_excel(io.BytesIO(content))
            else:
                df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

        df = df.where(pd.notnull(df), None)
        total_rows = len(df)

        job = MigrationJob(
            filename=file.filename,
            file_type=file_type.upper(),
            total_rows=total_rows,
            processed_rows=0,
            error_rows=0,
            status=MigrationStatus.UPLOADED.value,
            started_at=datetime.datetime.utcnow()
        )
        db.add(job)
        db.flush()

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            staging = MigrationStaging(
                job_id=job.id,
                row_number=int(idx) + 1,
                record_type=file_type.upper(),
                raw_data=json.dumps(row_dict),
                validation_status=StagingValidationStatus.PENDING.value
            )
            db.add(staging)

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def validate_job(db: Session, job_id: int) -> MigrationJob:
        job = db.query(MigrationJob).filter(MigrationJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Migration job not found")

        job.status = MigrationStatus.VALIDATING.value
        db.commit()

        # Clear existing errors for this job
        db.query(MigrationError).filter(MigrationError.job_id == job.id).delete()

        staging_records = db.query(MigrationStaging).filter(MigrationStaging.job_id == job.id).all()
        seen_keys = set()
        error_count = 0

        for record in staging_records:
            data = json.loads(record.raw_data)
            errors = []

            if job.file_type == "BOOKS":
                isbn = str(data.get("isbn") or data.get("ISBN") or "").strip()
                title = str(data.get("title") or data.get("Title") or "").strip()
                author = str(data.get("author") or data.get("Author") or "").strip()

                if not isbn:
                    errors.append(("isbn", "Missing mandatory field 'isbn'"))
                elif isbn in seen_keys:
                    errors.append(("isbn", f"Duplicate ISBN '{isbn}' within uploaded batch"))
                else:
                    seen_keys.add(isbn)
                    existing_db = db.query(Book).filter(Book.isbn == isbn).first()
                    if existing_db:
                        errors.append(("isbn", f"ISBN '{isbn}' already exists in operational database"))

                if not title:
                    errors.append(("title", "Missing mandatory field 'title'"))
                if not author:
                    errors.append(("author", "Missing mandatory field 'author'"))

            elif job.file_type == "MEMBERS":
                code = str(data.get("member_code") or data.get("code") or "").strip()
                email = str(data.get("email") or "").strip()
                name = str(data.get("full_name") or data.get("name") or "").strip()

                if not code:
                    errors.append(("member_code", "Missing mandatory field 'member_code'"))
                elif code in seen_keys:
                    errors.append(("member_code", f"Duplicate member_code '{code}' within batch"))
                else:
                    seen_keys.add(code)
                    existing_code = db.query(Member).filter(Member.member_code == code).first()
                    if existing_code:
                        errors.append(("member_code", f"Member code '{code}' already exists in database"))

                if not email or "@" not in email:
                    errors.append(("email", "Invalid or missing email address"))
                if not name:
                    errors.append(("full_name", "Missing mandatory field 'full_name'"))

            if errors:
                error_count += 1
                record.validation_status = StagingValidationStatus.INVALID.value
                record.error_message = "; ".join([f"{f}: {msg}" for f, msg in errors])
                for field_name, msg in errors:
                    err = MigrationError(
                        job_id=job.id,
                        row_number=record.row_number,
                        field_name=field_name,
                        error_reason=msg,
                        raw_record=record.raw_data
                    )
                    db.add(err)
            else:
                record.validation_status = StagingValidationStatus.VALID.value
                record.error_message = None

        job.error_rows = error_count
        job.status = MigrationStatus.VALIDATED.value
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def execute_migration(db: Session, job_id: int, user_id: Optional[int] = None) -> MigrationJob:
        job = db.query(MigrationJob).filter(MigrationJob.id == job_id).first()
        if not job or job.status != MigrationStatus.VALIDATED.value:
            raise HTTPException(status_code=400, detail="Job must be in VALIDATED state before execution.")

        valid_records = db.query(MigrationStaging).filter(
            MigrationStaging.job_id == job.id,
            MigrationStaging.validation_status == StagingValidationStatus.VALID.value
        ).all()

        migrated_count = 0
        for record in valid_records:
            data = json.loads(record.raw_data)
            if job.file_type == "BOOKS":
                book = Book(
                    isbn=str(data.get("isbn") or data.get("ISBN")),
                    title=str(data.get("title") or data.get("Title")),
                    author=str(data.get("author") or data.get("Author")),
                    publisher=data.get("publisher") or data.get("Publisher"),
                    publication_year=int(data.get("publication_year") or 2024) if data.get("publication_year") else None,
                    category=data.get("category") or data.get("Category") or "General",
                    description=data.get("description") or "Migrated from legacy records",
                    is_reference_only=bool(data.get("is_reference_only") or False),
                    total_copies=int(data.get("copies") or 1),
                    available_copies=int(data.get("copies") or 1)
                )
                db.add(book)
                db.flush()
                # Create book physical copies
                for i in range(1, book.total_copies + 1):
                    item = BookItem(
                        book_id=book.id,
                        accession_number=f"ACC-{book.isbn}-{i:02d}",
                        barcode=f"ACC-{book.isbn}-{i:02d}",
                        status=BookItemStatus.AVAILABLE.value,
                        shelf_location=f"STACK-{book.category[:3].upper() if book.category else 'GEN'}-01"
                    )
                    db.add(item)
            elif job.file_type == "MEMBERS":
                member = Member(
                    member_code=str(data.get("member_code") or data.get("code")),
                    full_name=str(data.get("full_name") or data.get("name")),
                    email=str(data.get("email")),
                    phone=str(data.get("phone") or ""),
                    department=data.get("department") or "General",
                    status=MemberStatus.ACTIVE.value,
                    max_borrow_limit=int(data.get("max_borrow_limit") or 4),
                    card_rfid_uid=data.get("card_rfid_uid")
                )
                db.add(member)

            record.validation_status = StagingValidationStatus.COMMITTED.value
            migrated_count += 1

        job.processed_rows = migrated_count
        job.status = MigrationStatus.EXECUTED.value
        job.completed_at = datetime.datetime.utcnow()

        AuditService.log_action(
            db=db,
            user_id=user_id,
            action="MIGRATION_EXECUTE",
            entity_type="MIGRATION_JOB",
            entity_id=str(job.id),
            details={"file": job.filename, "type": job.file_type, "migrated_rows": migrated_count}
        )

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def rollback_job(db: Session, job_id: int, user_id: Optional[int] = None) -> MigrationJob:
        job = db.query(MigrationJob).filter(MigrationJob.id == job_id).first()
        if not job or job.status != MigrationStatus.EXECUTED.value:
            raise HTTPException(status_code=400, detail="Only EXECUTED jobs can be rolled back.")

        committed_records = db.query(MigrationStaging).filter(
            MigrationStaging.job_id == job.id,
            MigrationStaging.validation_status == StagingValidationStatus.COMMITTED.value
        ).all()

        for record in committed_records:
            data = json.loads(record.raw_data)
            if job.file_type == "BOOKS":
                isbn = str(data.get("isbn") or data.get("ISBN"))
                book = db.query(Book).filter(Book.isbn == isbn).first()
                if book:
                    db.delete(book)
            elif job.file_type == "MEMBERS":
                code = str(data.get("member_code") or data.get("code"))
                member = db.query(Member).filter(Member.member_code == code).first()
                if member:
                    db.delete(member)
            record.validation_status = StagingValidationStatus.VALID.value

        job.status = MigrationStatus.ROLLED_BACK.value
        job.processed_rows = 0

        AuditService.log_action(
            db=db,
            user_id=user_id,
            action="MIGRATION_ROLLBACK",
            entity_type="MIGRATION_JOB",
            entity_id=str(job.id),
            details={"file": job.filename, "status": "ROLLED_BACK"}
        )

        db.commit()
        db.refresh(job)
        return job

