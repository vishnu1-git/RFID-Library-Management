import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.inventory import InventorySession, InventorySessionStatus, InventoryRead
from app.models.rfid import RFIDTag
from app.models.book import BookItem, BookItemStatus
from app.schemas.inventory import InventoryStartRequest, InventoryScanItem
from app.services.audit_service import AuditService


class InventoryService:
    @staticmethod
    def start_session(db: Session, req: InventoryStartRequest, user_id: Optional[int] = None) -> InventorySession:
        session = InventorySession(
            session_name=req.session_name,
            target_shelf=req.target_shelf,
            initiated_by_user_id=user_id,
            status=InventorySessionStatus.ACTIVE.value,
            total_scanned=0,
            missing_count=0,
            misplaced_count=0,
            start_time=datetime.datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def record_scan(db: Session, scan: InventoryScanItem) -> InventoryRead:
        session = db.query(InventorySession).filter(InventorySession.id == scan.session_id).first()
        if not session or session.status != InventorySessionStatus.ACTIVE.value:
            raise HTTPException(status_code=400, detail="Active inventory session not found.")

        tag = db.query(RFIDTag).filter(RFIDTag.epc == scan.epc).first()
        book_item = tag.book_item if tag else None
        
        expected_shelf = book_item.shelf_location if book_item else None
        is_misplaced = False
        if expected_shelf and scan.detected_shelf != expected_shelf:
            is_misplaced = True

        read = InventoryRead(
            session_id=session.id,
            epc=scan.epc,
            book_item_id=book_item.id if book_item else None,
            detected_shelf=scan.detected_shelf,
            expected_shelf=expected_shelf,
            is_misplaced=is_misplaced,
            read_time=datetime.datetime.utcnow()
        )
        db.add(read)

        session.total_scanned += 1
        if is_misplaced:
            session.misplaced_count += 1

        db.commit()
        db.refresh(read)
        return read

    @staticmethod
    def complete_session(db: Session, session_id: int) -> InventorySession:
        session = db.query(InventorySession).filter(InventorySession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Inventory session not found.")

        # Compute missing items if target shelf was specified
        if session.target_shelf:
            expected_items = db.query(BookItem).filter(
                BookItem.shelf_location == session.target_shelf,
                BookItem.status == BookItemStatus.AVAILABLE.value
            ).all()

            scanned_item_ids = {r.book_item_id for r in session.reads if r.book_item_id}
            missing = [item for item in expected_items if item.id not in scanned_item_ids]
            session.missing_count = len(missing)

        session.status = InventorySessionStatus.COMPLETED.value
        session.end_time = datetime.datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

