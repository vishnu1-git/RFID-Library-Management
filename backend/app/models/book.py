import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class BookItemStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ISSUED = "ISSUED"
    LOST = "LOST"
    MAINTENANCE = "MAINTENANCE"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    publisher = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    is_reference_only = Column(Boolean, default=False, nullable=False)
    total_copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    items = relationship("BookItem", back_populates="book", cascade="all, delete-orphan")


class BookItem(Base):
    __tablename__ = "book_items"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    accession_number = Column(String(64), unique=True, nullable=False, index=True)
    barcode = Column(String(64), unique=True, nullable=True, index=True)
    status = Column(String(20), default=BookItemStatus.AVAILABLE.value, nullable=False, index=True)
    shelf_location = Column(String(64), nullable=True, index=True)  # e.g., "A1-S2-B04"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="items")
    rfid_tag = relationship("RFIDTag", back_populates="book_item", uselist=False)
    circulations = relationship("Circulation", back_populates="book_item")
    inventory_reads = relationship("InventoryRead", back_populates="book_item")
