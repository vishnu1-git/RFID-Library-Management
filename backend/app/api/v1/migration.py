import json
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.migration import MigrationJob, MigrationError, MigrationStaging
from app.models.user import User
from app.schemas.migration import (
    MigrationJobResponse,
    MigrationJobDetailResponse,
    MigrationErrorResponse,
    MigrationExecuteRequest,
    MigrationRollbackRequest,
)
from app.services.migration_service import MigrationService
from app.core.permissions import get_current_active_user, require_roles

router = APIRouter()


@router.post("/upload", response_model=MigrationJobResponse)
def upload_file(
    file: UploadFile = File(...),
    file_type: str = Query("BOOKS", pattern="^(BOOKS|MEMBERS)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    return MigrationService.upload_and_stage(db, file, file_type)


@router.post("/validate/{job_id}", response_model=MigrationJobResponse)
def validate_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    return MigrationService.validate_job(db, job_id)


@router.post("/execute", response_model=MigrationJobResponse)
def execute_migration(
    req: MigrationExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    return MigrationService.execute_migration(db, req.job_id, user_id=current_user.id)


@router.post("/rollback", response_model=MigrationJobResponse)
def rollback_migration(
    req: MigrationRollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    return MigrationService.rollback_job(db, req.job_id, user_id=current_user.id)


@router.get("/jobs", response_model=List[MigrationJobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(MigrationJob).order_by(MigrationJob.id.desc()).all()


@router.get("/jobs/{job_id}", response_model=MigrationJobDetailResponse)
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    job = db.query(MigrationJob).filter(MigrationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")

    errors_out = [
        MigrationErrorResponse(
            id=err.id,
            row_number=err.row_number,
            field_name=err.field_name,
            error_reason=err.error_reason,
            raw_record=err.raw_record
        ) for err in job.errors
    ]

    sample_staging = []
    staging_rows = db.query(MigrationStaging).filter(MigrationStaging.job_id == job.id).limit(10).all()
    for s in staging_rows:
        try:
            d = json.loads(s.raw_data)
            d["_status"] = s.validation_status
            d["_error"] = s.error_message
            sample_staging.append(d)
        except Exception:
            pass

    return MigrationJobDetailResponse(
        id=job.id,
        filename=job.filename,
        file_type=job.file_type,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        error_rows=job.error_rows,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        errors=errors_out,
        sample_staging=sample_staging
    )
