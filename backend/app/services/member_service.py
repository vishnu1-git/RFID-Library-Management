from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from app.models.member import Member, MemberStatus
from app.schemas.member import MemberCreate, MemberUpdate


class MemberService:
    @staticmethod
    def get_members(db: Session, skip: int = 0, limit: int = 100, query: Optional[str] = None) -> List[Member]:
        q = db.query(Member)
        if query:
            search = f"%{query}%"
            q = q.filter(
                or_(
                    Member.full_name.ilike(search),
                    Member.member_code.ilike(search),
                    Member.email.ilike(search),
                    Member.department.ilike(search)
                )
            )
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def get_member_by_id(db: Session, member_id: int) -> Optional[Member]:
        return db.query(Member).filter(Member.id == member_id).first()

    @staticmethod
    def get_member_by_code(db: Session, code: str) -> Optional[Member]:
        return db.query(Member).filter(Member.member_code == code).first()

    @staticmethod
    def get_member_by_card_uid(db: Session, card_uid: str) -> Optional[Member]:
        return db.query(Member).filter(Member.card_rfid_uid == card_uid).first()

    @staticmethod
    def create_member(db: Session, member_in: MemberCreate) -> Member:
        if MemberService.get_member_by_code(db, member_in.member_code):
            raise HTTPException(status_code=400, detail="Member code already exists.")
        
        existing_email = db.query(Member).filter(Member.email == member_in.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Member with this email already exists.")

        member = Member(
            member_code=member_in.member_code,
            full_name=member_in.full_name,
            email=member_in.email,
            phone=member_in.phone,
            department=member_in.department,
            status=MemberStatus.ACTIVE.value,
            max_borrow_limit=member_in.max_borrow_limit,
            outstanding_fines=0.0,
            card_rfid_uid=member_in.card_rfid_uid
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def update_member_status(db: Session, member_id: int, status: str) -> Member:
        member = MemberService.get_member_by_id(db, member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        member.status = status
        db.commit()
        db.refresh(member)
        return member

