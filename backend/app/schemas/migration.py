import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class MigrationJobResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    total_rows: int
    processed_rows: int
    error_rows: int
    status: str
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class MigrationErrorResponse(BaseModel):
    id: int
    row_number: int
    field_name: Optional[str] = None
    error_reason: str
    raw_record: Optional[str] = None

    class Config:
        from_attributes = True


class MigrationJobDetailResponse(MigrationJobResponse):
    errors: List[MigrationErrorResponse] = []
    sample_staging: List[Dict[str, Any]] = []


class MigrationExecuteRequest(BaseModel):
    job_id: int


class MigrationRollbackRequest(BaseModel):
    job_id: int
