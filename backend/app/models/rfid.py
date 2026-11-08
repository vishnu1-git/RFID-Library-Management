import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class RFIDTag(Base):
    __tablename__ = "rfid_tags"

    id = Column(Integer, primary_key=True, index=True)
    epc = Column(String(64), unique=True, nullable=False, index=True)
    tid = Column(String(64), nullable=True)
    book_item_id = Column(Integer, ForeignKey("book_items.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    # security_bit: True = Arm / Secured (in-library, alarms if moved past gate); False = Disarmed (checked out)
    security_bit = Column(Boolean, default=True, nullable=False)
    last_seen_at = Column(DateTime, nullable=True)
    last_seen_reader = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    book_item = relationship("BookItem", back_populates="rfid_tag")
    gate_events = relationship("GateEvent", back_populates="rfid_tag")
