import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.circulation import Circulation, CirculationStatus
from app.models.book import Book, BookItem, BookItemStatus
from app.models.member import Member, MemberStatus
from app.models.rfid import RFIDTag
from app.models.notification import Notification, NotificationChannel
from app.schemas.circulation import CheckoutRequest, CheckinRequest, RenewRequest
from app.core.config import settings
from app.services.fine_service import FineService
from app.services.audit_service import AuditService


class CirculationService:
    @staticmethod
    def _resolve_book_item(db: Session, accession_number: Optional[str], book_item_id: Optional[int], epc: Optional[str]) -> BookItem:
        if epc:
            tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
            if not tag or not tag.book_item_id:
                raise HTTPException(status_code=404, detail=f"RFID Tag '{epc}' is not associated with any book copy.")
            item = db.query(BookItem).filter(BookItem.id == tag.book_item_id).first()
            if item:
                return item

        if book_item_id:
            item = db.query(BookItem).filter(BookItem.id == book_item_id).first()
            if item:
                return item

        if accession_number:
            item = db.query(BookItem).filter(BookItem.accession_number == accession_number).first()
            if item:
                return item

        raise HTTPException(status_code=400, detail="Must supply valid EPC, Accession Number, or Item ID.")

    @staticmethod
    def _resolve_member(db: Session, member_code: Optional[str], member_id: Optional[int], card_uid: Optional[str]) -> Member:
        if card_uid:
            member = db.query(Member).filter(Member.card_rfid_uid == card_uid).first()
            if member:
                return member

        if member_id:
            member = db.query(Member).filter(Member.id == member_id).first()
            if member:
                return member

        if member_code:
            member = db.query(Member).filter(Member.member_code == member_code).first()
            if member:
                return member

        raise HTTPException(status_code=400, detail="Must supply valid Member Code, ID, or Smart Card UID.")

    @staticmethod
    def checkout(db: Session, req: CheckoutRequest, operator_id: Optional[int] = None) -> Circulation:
        item = CirculationService._resolve_book_item(db, req.accession_number, req.book_item_id, req.epc)
        member = CirculationService._resolve_member(db, req.member_code, req.member_id, req.member_card_uid)
        book = item.book

        # AISYS Validation Rule 1: Reference books cannot be borrowed
        if book.is_reference_only:
            raise HTTPException(
                status_code=400,
                detail=f"Restriction Alert: '{book.title}' is marked as REFERENCE ONLY and cannot be circulated outside the library."
            )

        # AISYS Validation Rule 2: Blocked members cannot borrow books
        if member.status != MemberStatus.ACTIVE.value:
            raise HTTPException(
                status_code=400,
                detail=f"Restriction Alert: Member '{member.full_name}' account is {member.status} and ineligible for borrowing."
            )

        # AISYS Validation Rule 3: Fine limit violation
        if member.outstanding_fines >= settings.MAX_OVERDUE_FINE_LIMIT:
            raise HTTPException(
                status_code=400,
                detail=f"Restriction Alert: Member has unpaid fines of ${member.outstanding_fines:.2f}, exceeding the allowed limit."
            )

        # AISYS Validation Rule 4: Active borrow limit
        active_borrows = db.query(Circulation).filter(
            Circulation.member_id == member.id,
            Circulation.status == CirculationStatus.ISSUED.value
        ).count()
        if active_borrows >= member.max_borrow_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Borrowing limit reached: Member already has {active_borrows} books checked out (Max: {member.max_borrow_limit})."
            )

        # AISYS Validation Rule 5: Book copy already issued (prevents duplicate RFID event issue)
        if item.status == BookItemStatus.ISSUED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Conflict: Book copy '{item.accession_number}' is already currently ISSUED."
            )

        # Execute Checkout
        checkout_date = datetime.datetime.utcnow()
        due_date = checkout_date + datetime.timedelta(days=settings.DEFAULT_BORROW_DAYS)

        circulation = Circulation(
            book_item_id=item.id,
            member_id=member.id,
            issued_by_user_id=operator_id,
            checkout_date=checkout_date,
            due_date=due_date,
            renewal_count=0,
            status=CirculationStatus.ISSUED.value,
            notes=req.notes
        )
        db.add(circulation)

        # Update physical copy and book stats
        item.status = BookItemStatus.ISSUED.value
        book.available_copies = max(0, book.available_copies - 1)

        # Disarm RFID Tag for safe passage through security gate (security_bit = False)
        if item.rfid_tag:
            item.rfid_tag.security_bit = False  # DISARMED

        # Queue simulated checkout receipt notification
        notif = Notification(
            recipient=member.email,
            channel=NotificationChannel.EMAIL.value,
            event_type="CHECKOUT_RECEIPT",
            subject=f"Library Checkout Receipt: {book.title}",
            message_body=f"Dear {member.full_name}, you checked out '{book.title}' (Acc: {item.accession_number}). Due date: {due_date.strftime('%Y-%m-%d')}."
        )
        db.add(notif)

        # Audit log
        AuditService.log_action(
            db=db,
            user_id=operator_id,
            action="CHECKOUT",
            entity_type="CIRCULATION",
            entity_id=str(item.accession_number),
            details={"book_title": book.title, "member_code": member.member_code, "due_date": due_date.isoformat()}
        )

        db.commit()
        db.refresh(circulation)
        return circulation

    @staticmethod
    def checkin(db: Session, req: CheckinRequest, operator_id: Optional[int] = None) -> Circulation:
        item = CirculationService._resolve_book_item(db, req.accession_number, req.book_item_id, req.epc)
        book = item.book

        circulation = db.query(Circulation).filter(
            Circulation.book_item_id == item.id,
            Circulation.status == CirculationStatus.ISSUED.value
        ).order_by(Circulation.id.desc()).first()

        if not circulation:
            raise HTTPException(status_code=400, detail=f"Book copy '{item.accession_number}' is not recorded as issued.")

        return_date = datetime.datetime.utcnow()
        circulation.return_date = return_date
        circulation.status = CirculationStatus.RETURNED.value
        if req.notes:
            circulation.notes = f"{circulation.notes or ''} | Return note: {req.notes}"

        # Update physical copy and book stats
        item.status = BookItemStatus.AVAILABLE.value
        book.available_copies = min(book.total_copies, book.available_copies + 1)

        # Re-arm RFID Tag for in-library security protection (security_bit = True)
        if item.rfid_tag:
            item.rfid_tag.security_bit = True  # ARMED

        # Calculate overdue fines if any
        FineService.assess_circulation_fine(db, circulation)

        # Audit log
        AuditService.log_action(
            db=db,
            user_id=operator_id,
            action="CHECKIN",
            entity_type="CIRCULATION",
            entity_id=str(item.accession_number),
            details={"book_title": book.title, "return_date": return_date.isoformat()}
        )

        db.commit()
        db.refresh(circulation)
        return circulation

    @staticmethod
    def renew(db: Session, req: RenewRequest, operator_id: Optional[int] = None) -> Circulation:
        item = None
        if req.circulation_id:
            circulation = db.query(Circulation).filter(Circulation.id == req.circulation_id).first()
        else:
            item = CirculationService._resolve_book_item(db, req.accession_number, None, req.epc)
            circulation = db.query(Circulation).filter(
                Circulation.book_item_id == item.id,
                Circulation.status == CirculationStatus.ISSUED.value
            ).order_by(Circulation.id.desc()).first()

        if not circulation or circulation.status != CirculationStatus.ISSUED.value:
            raise HTTPException(status_code=400, detail="Active circulation record not found for renewal.")

        if circulation.renewal_count >= 2:
            raise HTTPException(status_code=400, detail="Maximum renewal limit (2 times) reached. Book must be returned.")

        circulation.renewal_count += 1
        circulation.due_date = circulation.due_date + datetime.timedelta(days=settings.DEFAULT_BORROW_DAYS)

        AuditService.log_action(
            db=db,
            user_id=operator_id,
            action="RENEW",
            entity_type="CIRCULATION",
            entity_id=str(circulation.id),
            details={"renewal_count": circulation.renewal_count, "new_due_date": circulation.due_date.isoformat()}
        )

        db.commit()
        db.refresh(circulation)
        return circulation
