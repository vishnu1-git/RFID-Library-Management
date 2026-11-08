from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.member import MemberCreate, MemberResponse, MemberUpdate
from app.services.member_service import MemberService
from app.core.permissions import get_current_active_user, require_roles

router = APIRouter()


@router.get("", response_model=List[MemberResponse])
def list_members(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    q: Optional[str] = None
):
    return MemberService.get_members(db, skip=skip, limit=limit, query=q)


@router.post("", response_model=MemberResponse)
def create_member(
    member_in: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Librarian"]))
):
    return MemberService.create_member(db, member_in)


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = MemberService.get_member_by_id(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.patch("/{member_id}/status", response_model=MemberResponse)
def update_status(
    member_id: int,
    status: str = Query(..., pattern="^(ACTIVE|BLOCKED|EXPIRED)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Librarian"]))
):
    return MemberService.update_member_status(db, member_id, status)
