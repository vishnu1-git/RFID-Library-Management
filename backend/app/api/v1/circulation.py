import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.circulation import Circulation, CirculationStatus, Fine, FineStatus
from app.models.user import User
from app.schemas.circulation import (
    CheckoutRequest,
    CheckinRequest,
    RenewRequest,
    CirculationResponse,
    FineResponse,
    FinePayRequest,
)
from app.services.circulation_service import CirculationService
from app.services.fine_service import FineService
from app.core.permissions import get_current_active_user, require_roles

router = APIRouter()


def _format_circ(circ: Circulation) -> CirculationResponse:
    now = datetime.datetime.utcnow()
    is_overdue = (circ.status == CirculationStatus.ISSUED.value and circ.due_date < now)
    accrued = FineService.calculate_overdue_fine(circ.due_date, circ.return_date) if is_overdue else 0.0

    return CirculationResponse(
        id=circ.id,
        book_item_id=circ.book_item_id,
        book_title=circ.book_item.book.title if circ.book_item else "Unknown",
        accession_number=circ.book_item.accession_number if circ.book_item else "Unknown",
        member_id=circ.member_id,
        member_name=circ.member.full_name if circ.member else "Unknown",
        member_code=circ.member.member_code if circ.member else "Unknown",
        issued_by_username=circ.operator.username if circ.operator else None,
        checkout_date=circ.checkout_date,
        due_date=circ.due_date,
        return_date=circ.return_date,
        renewal_count=circ.renewal_count,
        status=circ.status,
        is_overdue=is_overdue,
        accrued_fine=accrued
    )


@router.post("/checkout", response_model=CirculationResponse)
def checkout_book(
    req: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    circ = CirculationService.checkout(db, req, operator_id=current_user.id)
    return _format_circ(circ)


@router.post("/checkin", response_model=CirculationResponse)
def checkin_book(
    req: CheckinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    circ = CirculationService.checkin(db, req, operator_id=current_user.id)
    return _format_circ(circ)


@router.post("/renew", response_model=CirculationResponse)
def renew_book(
    req: RenewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    circ = CirculationService.renew(db, req, operator_id=current_user.id)
    return _format_circ(circ)


@router.get("/active", response_model=List[CirculationResponse])
def get_active_circulations(db: Session = Depends(get_db)):
    circs = db.query(Circulation).filter(
        Circulation.status == CirculationStatus.ISSUED.value
    ).order_by(Circulation.checkout_date.desc()).all()
    return [_format_circ(c) for c in circs]


@router.get("/history", response_model=List[CirculationResponse])
def get_circulation_history(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    circs = db.query(Circulation).order_by(Circulation.id.desc()).offset(skip).limit(limit).all()
    return [_format_circ(c) for c in circs]


@router.get("/fines", response_model=List[FineResponse])
def list_fines(
    status: Optional[str] = Query(None, pattern="^(UNPAID|PAID|WAIVED)$"),
    db: Session = Depends(get_db)
):
    q = db.query(Fine)
    if status:
        q = q.filter(Fine.status == status)
    fines = q.order_by(Fine.id.desc()).limit(100).all()
    results = []
    for f in fines:
        results.append(FineResponse(
            id=f.id,
            circulation_id=f.circulation_id,
            member_id=f.member_id,
            member_name=f.member.full_name if f.member else "Unknown",
            member_code=f.member.member_code if f.member else "Unknown",
            amount=f.amount,
            reason=f.reason,
            status=f.status,
            paid_at=f.paid_at,
            created_at=f.created_at
        ))
    return results


@router.post("/fines/settle", response_model=FineResponse)
def settle_fine(
    req: FinePayRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Librarian"]))
):
    f = FineService.settle_fine(db, req.fine_id, req.action)
    return FineResponse(
        id=f.id,
        circulation_id=f.circulation_id,
        member_id=f.member_id,
        member_name=f.member.full_name if f.member else "Unknown",
        member_code=f.member.member_code if f.member else "Unknown",
        amount=f.amount,
        reason=f.reason,
        status=f.status,
        paid_at=f.paid_at,
        created_at=f.created_at
    )
