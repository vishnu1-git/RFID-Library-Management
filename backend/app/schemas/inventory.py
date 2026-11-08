import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class InventoryStartRequest(BaseModel):
    session_name: str
    target_shelf: Optional[str] = None


class InventoryScanItem(BaseModel):
    session_id: int
    epc: str
    detected_shelf: str


class InventoryReadResponse(BaseModel):
    id: int
    epc: str
    book_title: Optional[str] = None
    accession_number: Optional[str] = None
    detected_shelf: str
    expected_shelf: Optional[str] = None
    is_misplaced: bool
    read_time: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class MissingBookItem(BaseModel):
    accession_number: str
    book_title: str
    expected_shelf: Optional[str] = None
    epc: Optional[str] = None


class InventorySessionResponse(BaseModel):
    id: int
    session_name: str
    target_shelf: Optional[str] = None
    status: str
    total_scanned: int
    missing_count: int
    misplaced_count: int
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InventorySessionDetailResponse(InventorySessionResponse):
    reads: List[InventoryReadResponse] = []
    missing_items: List[MissingBookItem] = []

