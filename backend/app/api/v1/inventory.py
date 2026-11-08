from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.inventory import InventorySession, InventoryRead
from app.models.book import BookItem, BookItemStatus
from app.models.user import User
from app.schemas.inventory import (
    InventoryStartRequest,
    InventoryScanItem,
    InventorySessionResponse,
    InventorySessionDetailResponse,
    InventoryReadResponse,
    MissingBookItem,
)
from app.services.inventory_service import InventoryService
from app.core.permissions import get_current_active_user

router = APIRouter()


@router.get("/sessions", response_model=List[InventorySessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(InventorySession).order_by(InventorySession.id.desc()).all()


@router.post("/start", response_model=InventorySessionResponse)
def start_inventory(
    req: InventoryStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return InventoryService.start_session(db, req, user_id=current_user.id)


@router.post("/scan", response_model=InventoryReadResponse)
def record_inventory_scan(
    scan: InventoryScanItem,
    db: Session = Depends(get_db)
):
    read = InventoryService.record_scan(db, scan)
    item = read.book_item
    return InventoryReadResponse(
        id=read.id,
        epc=read.epc,
        book_title=item.book.title if item and item.book else None,
        accession_number=item.accession_number if item else None,
        detected_shelf=read.detected_shelf,
        expected_shelf=read.expected_shelf,
        is_misplaced=read.is_misplaced,
        read_time=read.read_time
    )


@router.post("/{session_id}/complete", response_model=InventorySessionResponse)
def complete_inventory(session_id: int, db: Session = Depends(get_db)):
    return InventoryService.complete_session(db, session_id)


@router.get("/{session_id}/results", response_model=InventorySessionDetailResponse)
def get_inventory_results(session_id: int, db: Session = Depends(get_db)):
    session = db.query(InventorySession).filter(InventorySession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Inventory session not found")

    reads_out = []
    scanned_item_ids = set()
    for r in session.reads:
        if r.book_item_id:
            scanned_item_ids.add(r.book_item_id)
        item = r.book_item
        reads_out.append(InventoryReadResponse(
            id=r.id,
            epc=r.epc,
            book_title=item.book.title if item and item.book else None,
            accession_number=item.accession_number if item else None,
            detected_shelf=r.detected_shelf,
            expected_shelf=r.expected_shelf,
            is_misplaced=r.is_misplaced,
            read_time=r.read_time
        ))

    missing_items = []
    if session.target_shelf:
        expected = db.query(BookItem).filter(
            BookItem.shelf_location == session.target_shelf,
            BookItem.status == BookItemStatus.AVAILABLE.value
        ).all()
        for it in expected:
            if it.id not in scanned_item_ids:
                missing_items.append(MissingBookItem(
                    accession_number=it.accession_number,
                    book_title=it.book.title if it.book else "Unknown",
                    expected_shelf=it.shelf_location,
                    epc=it.rfid_tag.epc if it.rfid_tag else None
                ))

    return InventorySessionDetailResponse(
        id=session.id,
        session_name=session.session_name,
        target_shelf=session.target_shelf,
        status=session.status,
        total_scanned=session.total_scanned,
        missing_count=len(missing_items),
        misplaced_count=session.misplaced_count,
        start_time=session.start_time,
        end_time=session.end_time,
        reads=reads_out,
        missing_items=missing_items
    )

