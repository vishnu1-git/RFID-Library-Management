import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.rfid import RFIDTag
from app.models.book import BookItem
from app.models.member import Member
from app.models.user import User
from app.schemas.rfid import RFIDScanEvent, RFIDTagAssociate, RFIDTagResponse
from app.core.permissions import get_current_active_user, require_roles
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/scan")
def process_rfid_scan(event: RFIDScanEvent, db: Session = Depends(get_db)):
    """Device-neutral RFID scan ingestion endpoint."""
    epc = event.epc.strip()
    tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
    
    # 1. Check if EPC matches an item RFID tag
    if tag:
        tag.last_seen_at = datetime.datetime.utcnow()
        tag.last_seen_reader = event.reader_id
        db.commit()

        item = tag.book_item
        book = item.book if item else None
        return {
            "entity_type": "BOOK_TAG",
            "epc": epc,
            "security_bit": tag.security_bit,
            "is_armed": tag.security_bit,
            "book": {
                "id": book.id if book else None,
                "title": book.title if book else "Unknown",
                "author": book.author if book else "Unknown",
                "accession_number": item.accession_number if item else None,
                "shelf_location": item.shelf_location if item else None,
                "status": item.status if item else None,
                "is_reference_only": book.is_reference_only if book else False,
            } if item else None,
            "reader_id": event.reader_id
        }

    # 2. Check if EPC matches a Member Smart Card
    member = db.query(Member).filter(Member.card_rfid_uid == epc).first()
    if member:
        return {
            "entity_type": "MEMBER_CARD",
            "epc": epc,
            "member": {
                "id": member.id,
                "member_code": member.member_code,
                "full_name": member.full_name,
                "status": member.status,
                "outstanding_fines": member.outstanding_fines
            },
            "reader_id": event.reader_id
        }

    # 3. Check if EPC matches a Staff Smart Card
    staff = db.query(User).filter(User.smart_card_uid == epc).first()
    if staff:
        return {
            "entity_type": "STAFF_CARD",
            "epc": epc,
            "staff": {
                "id": staff.id,
                "username": staff.username,
                "full_name": staff.full_name,
            },
            "reader_id": event.reader_id
        }

    # 4. Unregistered blank tag
    return {
        "entity_type": "UNREGISTERED_TAG",
        "epc": epc,
        "reader_id": event.reader_id,
        "message": "Tag detected but not yet bound to any book item or member card."
    }


@router.post("/tag", response_model=RFIDTagResponse)
def associate_rfid_tag(
    req: RFIDTagAssociate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Librarian"]))
):
    """Enforces: Every active RFID tag is uniquely associated with one book copy."""
    epc = req.epc.strip()

    # Check if tag already exists and is bound
    existing_tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
    if existing_tag and existing_tag.book_item_id:
        raise HTTPException(status_code=400, detail=f"RFID EPC '{epc}' is already associated with book copy ID {existing_tag.book_item_id}.")

    # Resolve book item
    item = None
    if req.book_item_id:
        item = db.query(BookItem).filter(BookItem.id == req.book_item_id).first()
    elif req.accession_number:
        item = db.query(BookItem).filter(BookItem.accession_number == req.accession_number.strip()).first()

    if not item:
        raise HTTPException(status_code=404, detail="Target book copy not found.")

    if item.rfid_tag:
        raise HTTPException(status_code=400, detail=f"Book copy '{item.accession_number}' already has assigned RFID tag '{item.rfid_tag.epc}'.")

    if not existing_tag:
        existing_tag = RFIDTag(epc=epc, tid=req.tid)
        db.add(existing_tag)

    existing_tag.book_item_id = item.id
    existing_tag.security_bit = True  # Arm initially for inside library protection
    existing_tag.is_active = True
    existing_tag.last_seen_at = datetime.datetime.utcnow()
    existing_tag.last_seen_reader = "STAFF-TAG-WRITER-01"

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="RFID_TAG_ASSOCIATION",
        entity_type="RFID_TAG",
        entity_id=epc,
        details={"accession_number": item.accession_number, "book_title": item.book.title}
    )

    db.commit()
    db.refresh(existing_tag)

    return RFIDTagResponse(
        id=existing_tag.id,
        epc=existing_tag.epc,
        tid=existing_tag.tid,
        book_item_id=existing_tag.book_item_id,
        is_active=existing_tag.is_active,
        security_bit=existing_tag.security_bit,
        last_seen_at=existing_tag.last_seen_at,
        last_seen_reader=existing_tag.last_seen_reader,
        book_title=item.book.title,
        accession_number=item.accession_number
    )


@router.get("/tags", response_model=List[RFIDTagResponse])
def list_tags(db: Session = Depends(get_db)):
    tags = db.query(RFIDTag).order_by(RFIDTag.id.desc()).limit(100).all()
    results = []
    for t in tags:
        item = t.book_item
        book = item.book if item else None
        results.append(RFIDTagResponse(
            id=t.id,
            epc=t.epc,
            tid=t.tid,
            book_item_id=t.book_item_id,
            is_active=t.is_active,
            security_bit=t.security_bit,
            last_seen_at=t.last_seen_at,
            last_seen_reader=t.last_seen_reader,
            book_title=book.title if book else None,
            accession_number=item.accession_number if item else None
        ))
    return results
