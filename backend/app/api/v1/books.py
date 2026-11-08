from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.book import BookItem
from app.schemas.book import BookCreate, BookResponse, BookDetailResponse, BookItemCreate, BookItemResponse
from app.services.catalog_service import CatalogService
from app.core.permissions import get_current_active_user, require_roles

router = APIRouter()


@router.get("", response_model=List[BookResponse])
def list_books(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    q: Optional[str] = None
):
    return CatalogService.get_books(db, skip=skip, limit=limit, query=q)


@router.post("", response_model=BookResponse)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Librarian"]))
):
    return CatalogService.create_book(db, book_in)


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = CatalogService.get_book_by_id(db, book_id)
    if not book:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Enrich items with active EPC if tagged
    items_out = []
    for it in book.items:
        epc = it.rfid_tag.epc if it.rfid_tag else None
        items_out.append(BookItemResponse(
            id=it.id,
            book_id=it.book_id,
            accession_number=it.accession_number,
            barcode=it.barcode,
            shelf_location=it.shelf_location,
            status=it.status,
            created_at=it.created_at,
            epc=epc
        ))
    
    return BookDetailResponse(
        id=book.id,
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        publication_year=book.publication_year,
        category=book.category,
        description=book.description,
        is_reference_only=book.is_reference_only,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        created_at=book.created_at,
        items=items_out
    )


@router.post("/{book_id}/items", response_model=BookItemResponse)
def add_copy_item(
    book_id: int,
    item_in: BookItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Librarian"]))
):
    item = CatalogService.add_copy_item(db, book_id, item_in)
    return BookItemResponse(
        id=item.id,
        book_id=item.book_id,
        accession_number=item.accession_number,
        barcode=item.barcode,
        shelf_location=item.shelf_location,
        status=item.status,
        created_at=item.created_at,
        epc=None
    )
