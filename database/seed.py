"""
LibraSync Database Seeder Utility
Initializes roles, default admin and librarian accounts, sample books, members, and RFID tags.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.main import seed_initial_data


def run_seed():
    print("[*] Creating database schema tables...")
    Base.metadata.create_all(bind=engine)
    print("[*] Executing seed routine...")
    seed_initial_data()
    print("[SUCCESS] Database seeded successfully.")


if __name__ == "__main__":
    run_seed()
