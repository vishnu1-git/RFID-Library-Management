import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class MemberStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    member_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)
    status = Column(String(20), default=MemberStatus.ACTIVE.value, nullable=False)
    max_borrow_limit = Column(Integer, default=4, nullable=False)
    outstanding_fines = Column(Float, default=0.0, nullable=False)
    card_rfid_uid = Column(String(64), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    circulations = relationship("Circulation", back_populates="member")
    fines = relationship("Fine", back_populates="member")

