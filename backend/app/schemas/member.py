import datetime
from typing import Optional
from pydantic import BaseModel


class MemberBase(BaseModel):
    member_code: str
    full_name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    max_borrow_limit: int = 4
    card_rfid_uid: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    max_borrow_limit: Optional[int] = None
    card_rfid_uid: Optional[str] = None


class MemberResponse(MemberBase):
    id: int
    status: str
    outstanding_fines: float
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
