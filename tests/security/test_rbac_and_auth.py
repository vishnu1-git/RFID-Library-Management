"""
Security Test Suite: Argon2 Password Hashing, Signed JWT Tokens, and Contactless Smart Card RBAC
Satisfies AISYS AC 07.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend"))
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.session import SessionLocal
from app.models.user import User


def test_argon2_hashing():
    raw_pass = "SecureAdminPass2026!"
    hashed = get_password_hash(raw_pass)
    assert hashed.startswith("$argon2"), "Password must be hashed using state-of-the-art Argon2"
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_generation():
    token = create_access_token(subject="admin", role="Admin")
    assert token is not None
    assert len(token.split(".")) == 3, "JWT must consist of header.payload.signature"


def test_smart_card_rbac_lookup():
    db = SessionLocal()
    try:
        # Staff Admin card UID
        admin = db.query(User).filter(User.smart_card_uid == "CARD-STAFF-ADMIN-01").first()
        assert admin is not None
        assert admin.username == "admin"
        role_names = [ur.role.name for ur in admin.roles if ur.role]
        assert "Admin" in role_names

        # Staff Librarian card UID
        lib = db.query(User).filter(User.smart_card_uid == "CARD-STAFF-LIB-02").first()
        assert lib is not None
        assert lib.username == "librarian"
        role_names = [ur.role.name for ur in lib.roles if ur.role]
        assert "Librarian" in role_names
    finally:
        db.close()

