import datetime
from typing import Optional
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    member_code: Optional[str] = None
    member_id: Optional[int] = None
    member_card_uid: Optional[str] = None
    epc: Optional[str] = None
    accession_number: Optional[str] = None
    book_item_id: Optional[int] = None
    notes: Optional[str] = None


class CheckinRequest(BaseModel):
    epc: Optional[str] = None
    accession_number: Optional[str] = None
    book_item_id: Optional[int] = None
    notes: Optional[str] = None


class RenewRequest(BaseModel):
    circulation_id: Optional[int] = None
    epc: Optional[str] = None
    accession_number: Optional[str] = None


class CirculationResponse(BaseModel):
    id: int
    book_item_id: int
    book_title: str
    accession_number: str
    member_id: int
    member_name: str
    member_code: str
    issued_by_username: Optional[str] = None
    checkout_date: datetime.datetime
    due_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    renewal_count: int
    status: str
    is_overdue: bool
    accrued_fine: float = 0.0

    class Config:
        from_attributes = True


class FineResponse(BaseModel):
    id: int
    circulation_id: Optional[int] = None
    member_id: int
    member_name: str
    member_code: str
    amount: float
    reason: str
    status: str
    paid_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class FinePayRequest(BaseModel):
    fine_id: int
    action: str = "PAY"  # "PAY" or "WAIVE"

