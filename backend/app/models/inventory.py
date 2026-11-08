import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class InventorySessionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InventorySession(Base):
    __tablename__ = "inventory_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(100), nullable=False)
    target_shelf = Column(String(50), nullable=True)  # e.g., "A1-S2" or NULL for full library
    initiated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default=InventorySessionStatus.ACTIVE.value, nullable=False, index=True)
    total_scanned = Column(Integer, default=0, nullable=False)
    missing_count = Column(Integer, default=0, nullable=False)
    misplaced_count = Column(Integer, default=0, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)

    reads = relationship("InventoryRead", back_populates="session", cascade="all, delete-orphan")


class InventoryRead(Base):
    __tablename__ = "inventory_reads"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("inventory_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    epc = Column(String(64), nullable=False, index=True)
    book_item_id = Column(Integer, ForeignKey("book_items.id", ondelete="SET NULL"), nullable=True, index=True)
    detected_shelf = Column(String(64), nullable=False)
    expected_shelf = Column(String(64), nullable=True)
    is_misplaced = Column(Boolean, default=False, nullable=False)
    read_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    session = relationship("InventorySession", back_populates="reads")
    book_item = relationship("BookItem", back_populates="inventory_reads")

