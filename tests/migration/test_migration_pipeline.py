"""
Migration Test Suite: Staging, Duplicate Collision Detection, and Atomic Rollback
Satisfies AISYS AC 01 & AC 10.
"""
import pytest
import os
import sys
import io
import json
import pandas as pd
from fastapi import UploadFile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend"))
from app.db.session import SessionLocal
from app.models.migration import MigrationStatus, StagingValidationStatus
from app.models.book import Book
from app.services.migration_service import MigrationService


def test_migration_pipeline_and_rollback():
    db = SessionLocal()
    try:
        # Create a test Excel buffer in-memory with:
        # 1. New unique book
        # 2. Duplicate ISBN collision with existing DB Clean Code (978-0132350884)
        records = [
            {
                "isbn": "978-0596517748",
                "title": "JavaScript: The Good Parts",
                "author": "Douglas Crockford",
                "publisher": "O'Reilly",
                "publication_year": 2008,
                "category": "Computer Science",
                "copies": 2,
                "is_reference_only": False
            },
            {
                "isbn": "978-0132350884", # Existing Clean Code ISBN (Must be caught as collision)
                "title": "Clean Code (Collision Test)",
                "author": "Robert C. Martin",
                "publisher": "Prentice Hall",
                "publication_year": 2008,
                "category": "Computer Science",
                "copies": 1,
                "is_reference_only": False
            }
        ]
        excel_buffer = io.BytesIO()
        pd.DataFrame(records).to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        upload_file = UploadFile(filename="test_books.xlsx", file=excel_buffer)

        # 1. Upload and Stage
        job = MigrationService.upload_and_stage(db, upload_file, "BOOKS")
        assert job.total_rows == 2
        assert job.status == MigrationStatus.UPLOADED.value

        # 2. Validate
        validated_job = MigrationService.validate_job(db, job.id)
        assert validated_job.status == MigrationStatus.VALIDATED.value
        assert validated_job.error_rows == 1, "Duplicate ISBN collision must be recorded as 1 error row"

        # Check errors table
        assert len(validated_job.errors) == 1
        assert "already exists in operational database" in validated_job.errors[0].error_reason

        # 3. Execute Migration (Only valid record committed)
        executed_job = MigrationService.execute_migration(db, job.id, user_id=1)
        assert executed_job.status == MigrationStatus.EXECUTED.value
        assert executed_job.processed_rows == 1

        # Verify book exists in operational database
        migrated_book = db.query(Book).filter(Book.isbn == "978-0596517748").first()
        assert migrated_book is not None
        assert migrated_book.title == "JavaScript: The Good Parts"

        # 4. Rollback Migration (AC 10)
        rolled_back_job = MigrationService.rollback_job(db, job.id, user_id=1)
        assert rolled_back_job.status == MigrationStatus.ROLLED_BACK.value

        # Verify book is cleanly rolled back and no longer in database
        check_deleted = db.query(Book).filter(Book.isbn == "978-0596517748").first()
        assert check_deleted is None, "Rollback must remove migrated records"

    finally:
        db.close()

