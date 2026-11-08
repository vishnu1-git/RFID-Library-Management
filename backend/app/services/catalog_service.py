from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from app.models.book import Book, BookItem, BookItemStatus
from app.models.rfid import RFIDTag
from app.schemas.book import BookCreate, BookUpdate, BookItemCreate


class CatalogService:
    @staticmethod
    def get_books(db: Session, skip: int = 0, limit: int = 100, query: Optional[str] = None) -> List[Book]:
        q = db.query(Book)
        if query:
            search = f"%{query}%"
            q = q.filter(
                or_(
                    Book.title.ilike(search),
                    Book.author.ilike(search),
                    Book.isbn.ilike(search),
                    Book.category.ilike(search)
                )
            )
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def get_book_by_isbn(db: Session, isbn: str) -> Optional[Book]:
        return db.query(Book).filter(Book.isbn == isbn).first()

    @staticmethod
    def create_book(db: Session, book_in: BookCreate) -> Book:
        existing = CatalogService.get_book_by_isbn(db, book_in.isbn)
        if existing:
            raise HTTPException(status_code=400, detail=f"Book with ISBN '{book_in.isbn}' already exists.")

        book = Book(
            isbn=book_in.isbn,
            title=book_in.title,
            author=book_in.author,
            publisher=book_in.publisher,
            publication_year=book_in.publication_year,
            category=book_in.category,
            description=book_in.description,
            is_reference_only=book_in.is_reference_only,
            total_copies=book_in.total_copies,
            available_copies=book_in.total_copies
        )
        db.add(book)
        db.flush()

        # Automatically create physical copies (BookItems)
        for i in range(1, book_in.total_copies + 1):
            accession_number = f"ACC-{book.isbn}-{i:02d}"
            item = BookItem(
                book_id=book.id,
                accession_number=accession_number,
                barcode=accession_number,
                status=BookItemStatus.AVAILABLE.value,
                shelf_location=f"STACK-{book.category[:3].upper() if book.category else 'GEN'}-01"
            )
            db.add(item)

        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def add_copy_item(db: Session, book_id: int, item_in: BookItemCreate) -> BookItem:
        book = CatalogService.get_book_by_id(db, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        existing_item = db.query(BookItem).filter(BookItem.accession_number == item_in.accession_number).first()
        if existing_item:
            raise HTTPException(status_code=400, detail="Accession number must be unique.")

        item = BookItem(
            book_id=book.id,
            accession_number=item_in.accession_number,
            barcode=item_in.barcode or item_in.accession_number,
            shelf_location=item_in.shelf_location,
            status=BookItemStatus.AVAILABLE.value
        )
        book.total_copies += 1
        book.available_copies += 1
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

