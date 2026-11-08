import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.api.v1 import api_router
from app.models import (
    Role, User, UserRole, Book, BookItem, BookItemStatus,
    Member, MemberStatus, RFIDTag
)
from app.core.security import get_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("librasync")


def seed_initial_data():
    """Seeds foundational roles, admin user, mock hardware tags, and sample catalog."""
    db = SessionLocal()
    try:
        # 1. Seed Roles
        role_admin = db.query(Role).filter(Role.name == "Admin").first()
        if not role_admin:
            role_admin = Role(name="Admin", description="Full administrative access")
            db.add(role_admin)
        
        role_librarian = db.query(Role).filter(Role.name == "Librarian").first()
        if not role_librarian:
            role_librarian = Role(name="Librarian", description="Catalog and circulation staff")
            db.add(role_librarian)

        role_operator = db.query(Role).filter(Role.name == "Operator").first()
        if not role_operator:
            role_operator = Role(name="Operator", description="Desk operator for issue/return")
            db.add(role_operator)
        db.flush()

        # 2. Seed Admin User
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@librasync.edu",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
                smart_card_uid="CARD-STAFF-ADMIN-01"
            )
            db.add(admin_user)
            db.flush()
            db.add(UserRole(user_id=admin_user.id, role_id=role_admin.id))

        # 3. Seed Librarian User
        lib_user = db.query(User).filter(User.username == "librarian").first()
        if not lib_user:
            lib_user = User(
                username="librarian",
                email="librarian@librasync.edu",
                full_name="Chief Librarian",
                hashed_password=get_password_hash("lib123"),
                is_active=True,
                is_superuser=False,
                smart_card_uid="CARD-STAFF-LIB-02"
            )
            db.add(lib_user)
            db.flush()
            db.add(UserRole(user_id=lib_user.id, role_id=role_librarian.id))

        # 4. Seed Sample Books
        if db.query(Book).count() == 0:
            books_data = [
                {
                    "isbn": "978-0132350884",
                    "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
                    "author": "Robert C. Martin",
                    "publisher": "Prentice Hall",
                    "publication_year": 2008,
                    "category": "Computer Science",
                    "description": "Fundamental software craftsmanship practices and architecture.",
                    "is_reference_only": False,
                    "total_copies": 3,
                },
                {
                    "isbn": "978-0201633610",
                    "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
                    "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
                    "publisher": "Addison-Wesley",
                    "publication_year": 1994,
                    "category": "Computer Science",
                    "description": "Classic 23 design patterns for object-oriented software engineering.",
                    "is_reference_only": False,
                    "total_copies": 2,
                },
                {
                    "isbn": "978-0198534532",
                    "title": "Oxford Reference Encyclopedia of Science & Technology",
                    "author": "Oxford University Press",
                    "publisher": "Oxford",
                    "publication_year": 2021,
                    "category": "Reference",
                    "description": "Comprehensive reference work for physical and applied sciences.",
                    "is_reference_only": True,  # Reference only (cannot be borrowed)
                    "total_copies": 1,
                },
                {
                    "isbn": "978-0321125217",
                    "title": "Domain-Driven Design: Tackling Complexity in the Heart of Software",
                    "author": "Eric Evans",
                    "publisher": "Addison-Wesley",
                    "publication_year": 2003,
                    "category": "Architecture",
                    "description": "Exploration of strategic and tactical domain modelling.",
                    "is_reference_only": False,
                    "total_copies": 2,
                }
            ]

            sample_epcs = [
                "E20034120123456789010001",
                "E20034120123456789010002",
                "E20034120123456789010003",
                "E20034120123456789010004",
                "E20034120123456789010005",
                "E20034120123456789010006",
                "E20034120123456789010007",
                "E20034120123456789010008",
            ]
            epc_idx = 0

            for b_data in books_data:
                b = Book(
                    isbn=b_data["isbn"],
                    title=b_data["title"],
                    author=b_data["author"],
                    publisher=b_data["publisher"],
                    publication_year=b_data["publication_year"],
                    category=b_data["category"],
                    description=b_data["description"],
                    is_reference_only=b_data["is_reference_only"],
                    total_copies=b_data["total_copies"],
                    available_copies=b_data["total_copies"]
                )
                db.add(b)
                db.flush()

                for c_num in range(1, b.total_copies + 1):
                    acc = f"ACC-{b.isbn[-4:]}-{c_num:02d}"
                    shelf = f"SHELF-{b.category[:3].upper() if b.category else 'GEN'}-01"
                    item = BookItem(
                        book_id=b.id,
                        accession_number=acc,
                        barcode=acc,
                        status=BookItemStatus.AVAILABLE.value,
                        shelf_location=shelf
                    )
                    db.add(item)
                    db.flush()

                    if epc_idx < len(sample_epcs):
                        tag = RFIDTag(
                            epc=sample_epcs[epc_idx],
                            tid=f"TID-9000{epc_idx:02d}",
                            book_item_id=item.id,
                            is_active=True,
                            security_bit=True,  # Armed (in-library)
                            last_seen_reader="STAFF-DESK-01"
                        )
                        db.add(tag)
                        epc_idx += 1

        # 5. Seed Sample Members
        if db.query(Member).count() == 0:
            members_data = [
                {
                    "member_code": "MEM-2026-001",
                    "full_name": "Aarav Sharma",
                    "email": "aarav.sharma@campus.edu",
                    "phone": "+91 98765 43210",
                    "department": "Computer Science",
                    "status": MemberStatus.ACTIVE.value,
                    "max_borrow_limit": 4,
                    "outstanding_fines": 0.0,
                    "card_rfid_uid": "CARD-MEM-STU-001"
                },
                {
                    "member_code": "MEM-2026-002",
                    "full_name": "Diya Patel",
                    "email": "diya.patel@campus.edu",
                    "phone": "+91 98765 43211",
                    "department": "Information Science",
                    "status": MemberStatus.ACTIVE.value,
                    "max_borrow_limit": 4,
                    "outstanding_fines": 0.0,
                    "card_rfid_uid": "CARD-MEM-STU-002"
                },
                {
                    "member_code": "MEM-2026-003",
                    "full_name": "Rohan Verma (Blocked)",
                    "email": "rohan.verma@campus.edu",
                    "phone": "+91 98765 43212",
                    "department": "Mechanical Eng",
                    "status": MemberStatus.BLOCKED.value,  # Blocked member (cannot borrow)
                    "max_borrow_limit": 4,
                    "outstanding_fines": 150.0,
                    "card_rfid_uid": "CARD-MEM-STU-003"
                }
            ]
            for m_data in members_data:
                m = Member(**m_data)
                db.add(m)

        db.commit()
        logger.info("Database schema verified and sample data seeded successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
    finally:
        db.close()


# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade RFID-Enabled Intelligent Library Management System (ILMS)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check():
    db_status = "connected"
    db_type = "PostgreSQL" if "postgresql" in str(engine.url) else "SQLite (Dev Fallback)"
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": {
            "status": db_status,
            "type": db_type,
            "url": str(engine.url).split("@")[-1]
        },
        "rfid_middleware": {
            "status": "active",
            "mode": "device_neutral_adapter"
        }
    }


# Mount API V1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)
