import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class BookItemBase(BaseModel):
    accession_number: str
    barcode: Optional[str] = None
    shelf_location: Optional[str] = "A1-S1-01"


class BookItemCreate(BookItemBase):
    pass


class BookItemResponse(BookItemBase):
    id: int
    book_id: int
    status: str
    created_at: datetime.datetime
    epc: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    category: Optional[str] = "General"
    description: Optional[str] = None
    is_reference_only: bool = False


class BookCreate(BookBase):
    total_copies: int = 1


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_reference_only: Optional[bool] = None


class BookResponse(BookBase):
    id: int
    total_copies: int
    available_copies: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class BookDetailResponse(BookResponse):
    items: List[BookItemResponse] = []

