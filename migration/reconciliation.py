"""
LibraSync Data Migration - Reconciliation Engine
Compares staged spreadsheet records against the operational database to generate reconciliation metrics
and discrepancy reports prior to commitment (AISYS SOP pages 1, 3 & 5).
"""
import json
import sys
import os
from typing import Dict, Any, List
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
from app.db.session import SessionLocal
from app.models.migration import MigrationJob, MigrationStaging, StagingValidationStatus
from app.models.book import Book
from app.models.member import Member


def reconcile_job(job_id: int) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        job = db.query(MigrationJob).filter(MigrationJob.id == job_id).first()
        if not job:
            return {"error": f"Job #{job_id} not found."}

        staged_rows = db.query(MigrationStaging).filter(MigrationStaging.job_id == job.id).all()
        
        reconciliation_report = {
            "job_id": job.id,
            "filename": job.filename,
            "file_type": job.file_type,
            "total_staged": len(staged_rows),
            "valid_new_records": 0,
            "existing_in_database": 0,
            "validation_failures": 0,
            "discrepancies": []
        }

        for record in staged_rows:
            data = json.loads(record.raw_data)
            if job.file_type == "BOOKS":
                isbn = str(data.get("isbn") or data.get("ISBN") or "").strip()
                existing = db.query(Book).filter(Book.isbn == isbn).first() if isbn else None
                if existing:
                    reconciliation_report["existing_in_database"] += 1
                    reconciliation_report["discrepancies"].append({
                        "row": record.row_number,
                        "type": "COLLISION_EXISTING_ISBN",
                        "identifier": isbn,
                        "existing_title": existing.title,
                        "staged_title": data.get("title") or data.get("Title"),
                        "action": "SKIP_TO_PRESERVE_DATABASE_INTEGRITY"
                    })
                elif record.validation_status == StagingValidationStatus.VALID.value:
                    reconciliation_report["valid_new_records"] += 1
                else:
                    reconciliation_report["validation_failures"] += 1

            elif job.file_type == "MEMBERS":
                code = str(data.get("member_code") or data.get("code") or "").strip()
                existing = db.query(Member).filter(Member.member_code == code).first() if code else None
                if existing:
                    reconciliation_report["existing_in_database"] += 1
                    reconciliation_report["discrepancies"].append({
                        "row": record.row_number,
                        "type": "COLLISION_EXISTING_MEMBER_CODE",
                        "identifier": code,
                        "existing_name": existing.full_name,
                        "staged_name": data.get("full_name") or data.get("name"),
                        "action": "SKIP_TO_PRESERVE_DATABASE_INTEGRITY"
                    })
                elif record.validation_status == StagingValidationStatus.VALID.value:
                    reconciliation_report["valid_new_records"] += 1
                else:
                    reconciliation_report["validation_failures"] += 1

        return reconciliation_report
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reconciliation.py <job_id>")
        sys.exit(1)
    
    jid = int(sys.argv[1])
    report = reconcile_job(jid)
    print(json.dumps(report, indent=2))

