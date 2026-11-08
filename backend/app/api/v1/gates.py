from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.gate import GateEvent
from app.models.user import User
from app.schemas.gate import GateEventCreate, GateEventResponse, GateEventResolve
from app.services.gate_service import GateService
from app.core.permissions import get_current_active_user

router = APIRouter()


@router.post("/events", response_model=GateEventResponse)
def trigger_gate_event(event_in: GateEventCreate, db: Session = Depends(get_db)):
    event = GateService.process_gate_event(db, event_in)
    tag = event.rfid_tag
    item = tag.book_item if tag else None
    book = item.book if item else None

    return GateEventResponse(
        id=event.id,
        reader_id=event.reader_id,
        epc=event.epc,
        book_title=book.title if book else None,
        accession_number=item.accession_number if item else None,
        is_authorized=event.is_authorized,
        alarm_triggered=event.alarm_triggered,
        cctv_snapshot_url=event.cctv_snapshot_url,
        timestamp=event.timestamp,
        resolved=event.resolved,
        notes=event.notes
    )


@router.get("/events", response_model=List[GateEventResponse])
def list_gate_events(db: Session = Depends(get_db)):
    events = db.query(GateEvent).order_by(GateEvent.id.desc()).limit(100).all()
    results = []
    for ev in events:
        tag = ev.rfid_tag
        item = tag.book_item if tag else None
        book = item.book if item else None
        results.append(GateEventResponse(
            id=ev.id,
            reader_id=ev.reader_id,
            epc=ev.epc,
            book_title=book.title if book else None,
            accession_number=item.accession_number if item else None,
            is_authorized=ev.is_authorized,
            alarm_triggered=ev.alarm_triggered,
            cctv_snapshot_url=ev.cctv_snapshot_url,
            timestamp=ev.timestamp,
            resolved=ev.resolved,
            notes=ev.notes
        ))
    return results


@router.post("/events/{event_id}/resolve", response_model=GateEventResponse)
def resolve_gate_event(
    event_id: int,
    req: GateEventResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ev = db.query(GateEvent).filter(GateEvent.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Gate event not found")

    ev.resolved = True
    ev.resolved_by_user_id = current_user.id
    ev.notes = req.notes
    db.commit()
    db.refresh(ev)

    tag = ev.rfid_tag
    item = tag.book_item if tag else None
    book = item.book if item else None

    return GateEventResponse(
        id=ev.id,
        reader_id=ev.reader_id,
        epc=ev.epc,
        book_title=book.title if book else None,
        accession_number=item.accession_number if item else None,
        is_authorized=ev.is_authorized,
        alarm_triggered=ev.alarm_triggered,
        cctv_snapshot_url=ev.cctv_snapshot_url,
        timestamp=ev.timestamp,
        resolved=ev.resolved,
        notes=ev.notes
    )
