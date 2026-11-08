import datetime
from typing import Optional
from pydantic import BaseModel


class GateEventCreate(BaseModel):
    reader_id: str = "GATE-MAIN-01"
    epc: str
    timestamp: Optional[datetime.datetime] = None


class GateEventResponse(BaseModel):
    id: int
    reader_id: str
    epc: str
    book_title: Optional[str] = None
    accession_number: Optional[str] = None
    is_authorized: bool
    alarm_triggered: bool
    cctv_snapshot_url: Optional[str] = None
    timestamp: datetime.datetime
    resolved: bool
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class GateEventResolve(BaseModel):
    event_id: int
    notes: Optional[str] = "Checked out manually / false alarm verified by security"

