import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
import enum
from app.db.base import Base


class NotificationChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PRINT = "PRINT"


class NotificationStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    SENT = "SENT"
    FAILED = "FAILED"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String(255), nullable=False)
    channel = Column(String(20), default=NotificationChannel.EMAIL.value, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    subject = Column(String(255), nullable=True)
    message_body = Column(Text, nullable=False)
    status = Column(String(20), default=NotificationStatus.QUEUED.value, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
