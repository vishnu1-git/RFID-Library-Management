"""
LibraSync Data Migration - Duplicate Detector Module
Detects intra-batch collisions and collisions against existing operational database records.
Enforces AISYS core safety principle: Existing ILMS records must not be overwritten.
"""
from typing import Set, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
from app.models.book import Book
from app.models.member import Member


class DuplicateDetector:
    def __init__(self, db: Session):
        self.db = db
        self.batch_isbns: Set[str] = set()
        self.batch_member_codes: Set[str] = set()

    def check_book_duplicate(self, isbn: str, row_num: int) -> List[Tuple[str, str]]:
        errors = []
        clean_isbn = isbn.strip()
        if not clean_isbn:
            return errors

        # 1. Intra-batch collision check
        if clean_isbn in self.batch_isbns:
            errors.append(("isbn", f"Row {row_num}: Duplicate ISBN '{clean_isbn}' within this upload batch."))
        else:
            self.batch_isbns.add(clean_isbn)

        # 2. Operational database collision check
        existing = self.db.query(Book).filter(Book.isbn == clean_isbn).first()
        if existing:
            errors.append(("isbn", f"Row {row_num}: ISBN '{clean_isbn}' already exists in operational database (Title: '{existing.title}'). Overwrite prohibited."))

        return errors

    def check_member_duplicate(self, code: str, row_num: int) -> List[Tuple[str, str]]:
        errors = []
        clean_code = code.strip()
        if not clean_code:
            return errors

        # 1. Intra-batch collision check
        if clean_code in self.batch_member_codes:
            errors.append(("member_code", f"Row {row_num}: Duplicate member code '{clean_code}' within this batch."))
        else:
            self.batch_member_codes.add(clean_code)

        # 2. Operational database collision check
        existing = self.db.query(Member).filter(Member.member_code == clean_code).first()
        if existing:
            errors.append(("member_code", f"Row {row_num}: Member code '{clean_code}' already exists in operational database ('{existing.full_name}'). Overwrite prohibited."))

        return errors

