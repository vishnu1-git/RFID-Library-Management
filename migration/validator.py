"""
LibraSync Data Migration - Validator Module
Validates spreadsheet records against mandatory schema requirements before committing to database.
"""
from typing import Dict, Any, List, Tuple


class MigrationValidator:
    @staticmethod
    def validate_book_record(data: Dict[str, Any], row_num: int) -> List[Tuple[str, str]]:
        errors = []
        isbn = str(data.get("isbn") or data.get("ISBN") or "").strip()
        title = str(data.get("title") or data.get("Title") or "").strip()
        author = str(data.get("author") or data.get("Author") or "").strip()

        if not isbn:
            errors.append(("isbn", f"Row {row_num}: Missing mandatory ISBN."))
        elif len(isbn) < 10:
            errors.append(("isbn", f"Row {row_num}: Invalid ISBN format '{isbn}' (minimum 10 characters)."))

        if not title:
            errors.append(("title", f"Row {row_num}: Missing mandatory Title."))

        if not author:
            errors.append(("author", f"Row {row_num}: Missing mandatory Author."))

        return errors

    @staticmethod
    def validate_member_record(data: Dict[str, Any], row_num: int) -> List[Tuple[str, str]]:
        errors = []
        code = str(data.get("member_code") or data.get("code") or "").strip()
        name = str(data.get("full_name") or data.get("name") or "").strip()
        email = str(data.get("email") or "").strip()

        if not code:
            errors.append(("member_code", f"Row {row_num}: Missing mandatory Member Code."))

        if not name:
            errors.append(("full_name", f"Row {row_num}: Missing mandatory Full Name."))

        if not email or "@" not in email:
            errors.append(("email", f"Row {row_num}: Invalid or missing email address '{email}'."))

        return errors

