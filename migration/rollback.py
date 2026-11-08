"""
LibraSync Data Migration - Rollback Engine
Performs atomic rollback of migrated records for a specific job (AC 10 Recovery).
"""
import sys
import os
import json
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
from app.db.session import SessionLocal
from app.services.migration_service import MigrationService


def execute_rollback(job_id: int):
    db: Session = SessionLocal()
    try:
        print(f"[*] Executing atomic rollback for Migration Job #{job_id}...")
        job = MigrationService.rollback_job(db, job_id)
        print(f"[SUCCESS] Migration Job #{job_id} rolled back successfully. Status: {job.status}")
        return True
    except Exception as e:
        print(f"[ERROR] Rollback failed: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rollback.py <job_id>")
        sys.exit(1)

    jid = int(sys.argv[1])
    execute_rollback(jid)
