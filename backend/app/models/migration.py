import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class MigrationStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    EXECUTED = "EXECUTED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class StagingValidationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID = "INVALID"
    COMMITTED = "COMMITTED"


class MigrationJob(Base):
    __tablename__ = "migration_jobs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # "BOOKS", "MEMBERS"
    total_rows = Column(Integer, default=0, nullable=False)
    processed_rows = Column(Integer, default=0, nullable=False)
    error_rows = Column(Integer, default=0, nullable=False)
    status = Column(String(30), default=MigrationStatus.UPLOADED.value, nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    staging_records = relationship("MigrationStaging", back_populates="job", cascade="all, delete-orphan")
    errors = relationship("MigrationError", back_populates="job", cascade="all, delete-orphan")


class MigrationStaging(Base):
    __tablename__ = "migration_staging"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("migration_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    record_type = Column(String(50), nullable=False)
    raw_data = Column(Text, nullable=False)  # JSON string of the uploaded row
    validation_status = Column(String(30), default=StagingValidationStatus.PENDING.value, nullable=False, index=True)
    error_message = Column(Text, nullable=True)

    job = relationship("MigrationJob", back_populates="staging_records")


class MigrationError(Base):
    __tablename__ = "migration_errors"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("migration_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    field_name = Column(String(100), nullable=True)
    error_reason = Column(Text, nullable=False)
    raw_record = Column(Text, nullable=True)

    job = relationship("MigrationJob", back_populates="errors")
