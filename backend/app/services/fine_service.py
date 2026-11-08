import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.circulation import Fine, FineStatus, Circulation
from app.models.member import Member
from app.core.config import settings


class FineService:
    @staticmethod
    def calculate_overdue_fine(due_date: datetime.datetime, return_date: Optional[datetime.datetime] = None) -> float:
        check_time = return_date or datetime.datetime.utcnow()
        if check_time <= due_date:
            return 0.0
        delta = check_time - due_date
        overdue_days = delta.days
        if delta.seconds > 0:
            overdue_days += 1
        return round(float(overdue_days * settings.FINE_PER_DAY), 2)

    @staticmethod
    def assess_circulation_fine(db: Session, circulation: Circulation) -> Optional[Fine]:
        fine_amount = FineService.calculate_overdue_fine(circulation.due_date, circulation.return_date)
        if fine_amount <= 0:
            return None

        fine = Fine(
            circulation_id=circulation.id,
            member_id=circulation.member_id,
            amount=fine_amount,
            reason=f"Overdue return ({fine_amount / settings.FINE_PER_DAY:.0f} days late)",
            status=FineStatus.UNPAID.value
        )
        db.add(fine)

        # Update member outstanding fines
        member = db.query(Member).filter(Member.id == circulation.member_id).first()
        if member:
            member.outstanding_fines += fine_amount
            if member.outstanding_fines >= settings.MAX_OVERDUE_FINE_LIMIT:
                member.status = "BLOCKED"

        db.commit()
        db.refresh(fine)
        return fine

    @staticmethod
    def settle_fine(db: Session, fine_id: int, action: str = "PAY") -> Fine:
        fine = db.query(Fine).filter(Fine.id == fine_id).first()
        if not fine:
            raise HTTPException(status_code=404, detail="Fine not found")

        if fine.status != FineStatus.UNPAID.value:
            raise HTTPException(status_code=400, detail="Fine is already settled")

        member = db.query(Member).filter(Member.id == fine.member_id).first()
        if action == "PAY":
            fine.status = FineStatus.PAID.value
            fine.paid_at = datetime.datetime.utcnow()
            if member:
                member.outstanding_fines = max(0.0, member.outstanding_fines - fine.amount)
        elif action == "WAIVE":
            fine.status = FineStatus.WAIVED.value
            if member:
                member.outstanding_fines = max(0.0, member.outstanding_fines - fine.amount)
        else:
            raise HTTPException(status_code=400, detail="Invalid settlement action")

        # Unblock member if fines cleared below limit
        if member and member.status == "BLOCKED" and member.outstanding_fines < settings.MAX_OVERDUE_FINE_LIMIT:
            member.status = "ACTIVE"

        db.commit()
        db.refresh(fine)
        return fine

