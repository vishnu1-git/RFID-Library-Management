import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class CirculationStatus(str, enum.Enum):
    ISSUED = "ISSUED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class FineStatus(str, enum.Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    WAIVED = "WAIVED"


class Circulation(Base):
    __tablename__ = "circulation"

    id = Column(Integer, primary_key=True, index=True)
    book_item_id = Column(Integer, ForeignKey("book_items.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    issued_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    checkout_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    return_date = Column(DateTime, nullable=True)
    renewal_count = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default=CirculationStatus.ISSUED.value, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    book_item = relationship("BookItem", back_populates="circulations")
    member = relationship("Member", back_populates="circulations")
    operator = relationship("User", back_populates="circulations")
    fines = relationship("Fine", back_populates="circulation")


class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)
    circulation_id = Column(Integer, ForeignKey("circulation.id", ondelete="SET NULL"), nullable=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)  # Overdue, Damaged book, Lost tag
    status = Column(String(20), default=FineStatus.UNPAID.value, nullable=False, index=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    circulation = relationship("Circulation", back_populates="fines")
    member = relationship("Member", back_populates="fines")

