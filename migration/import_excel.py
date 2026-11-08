"""
LibraSync Data Migration - Import Excel CLI
Staging pipeline ingesting Excel/CSV files into migration_staging for validation.
"""
import io
import json
import os
import sys
import datetime
import pandas as pd
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
from app.db.session import SessionLocal
from app.models.migration import MigrationJob, MigrationStaging, MigrationStatus, StagingValidationStatus


def stage_excel_file(filepath: str, file_type: str = "BOOKS") -> int:
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return -1

    filename = os.path.basename(filepath)
    print(f"[*] Reading '{filename}' for staging into LibraSync operational buffer...")

    if filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    df = df.where(pd.notnull(df), None)
    total_rows = len(df)
    print(f"[+] Found {total_rows} rows. Initializing MigrationJob record...")

    db: Session = SessionLocal()
    try:
        job = MigrationJob(
            filename=filename,
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
        print(f"[SUCCESS] Migration Job #{job.id} created with {total_rows} staged rows.")
        return job.id
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Staging failed: {e}")
        return -1
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_excel.py <path_to_excel_file> [BOOKS|MEMBERS]")
        sys.exit(1)

    path = sys.argv[1]
    ftype = sys.argv[2] if len(sys.argv) > 2 else "BOOKS"
    stage_excel_file(path, ftype)

