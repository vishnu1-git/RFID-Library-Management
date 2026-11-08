import datetime
from typing import Optional
from pydantic import BaseModel


class RFIDScanEvent(BaseModel):
    event_id: Optional[str] = None
    reader_id: str
    event_type: str = "TAG_DETECTED"
    epc: str
    timestamp: Optional[datetime.datetime] = None


class RFIDTagAssociate(BaseModel):
    epc: str
    accession_number: Optional[str] = None
    book_item_id: Optional[int] = None
    tid: Optional[str] = None


class RFIDTagResponse(BaseModel):
    id: int
    epc: str
    tid: Optional[str] = None
    book_item_id: Optional[int] = None
    is_active: bool
    security_bit: bool
    last_seen_at: Optional[datetime.datetime] = None
    last_seen_reader: Optional[str] = None
    book_title: Optional[str] = None
    accession_number: Optional[str] = None

    class Config:
        from_attributes = True

