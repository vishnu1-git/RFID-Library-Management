import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class GateEvent(Base):
    __tablename__ = "gate_events"

    id = Column(Integer, primary_key=True, index=True)
    reader_id = Column(String(64), nullable=False, default="GATE-MAIN-01", index=True)
    epc = Column(String(64), ForeignKey("rfid_tags.epc", ondelete="CASCADE"), nullable=False, index=True)
    book_item_id = Column(Integer, ForeignKey("book_items.id", ondelete="SET NULL"), nullable=True, index=True)
    is_authorized = Column(Boolean, default=False, nullable=False, index=True)
    alarm_triggered = Column(Boolean, default=True, nullable=False, index=True)
    cctv_snapshot_url = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)

    rfid_tag = relationship("RFIDTag", back_populates="gate_events")

