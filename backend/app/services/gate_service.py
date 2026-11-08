import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.gate import GateEvent
from app.models.rfid import RFIDTag
from app.models.book import BookItem
from app.models.notification import Notification, NotificationChannel
from app.schemas.gate import GateEventCreate
from app.services.audit_service import AuditService


class GateService:
    @staticmethod
    def process_gate_event(db: Session, event_in: GateEventCreate) -> GateEvent:
        tag = db.query(RFIDTag).filter(RFIDTag.epc == event_in.epc).first()
        book_item_id = tag.book_item_id if tag else None
        
        # Unauthorized if tag not registered OR if tag security bit is ARMED (True)
        is_authorized = bool(tag and not tag.security_bit)
        alarm_triggered = not is_authorized
        now = event_in.timestamp or datetime.datetime.utcnow()
        
        cctv_snapshot = None
        if alarm_triggered:
            cctv_snapshot = f"https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=400&q=80&event={now.timestamp()}"

        gate_event = GateEvent(
            reader_id=event_in.reader_id,
            epc=event_in.epc,
            book_item_id=book_item_id,
            is_authorized=is_authorized,
            alarm_triggered=alarm_triggered,
            cctv_snapshot_url=cctv_snapshot,
            timestamp=now,
            resolved=not alarm_triggered
        )
        db.add(gate_event)

        if alarm_triggered:
            item_desc = "Unknown Item"
            if tag and tag.book_item:
                item_desc = f"'{tag.book_item.book.title}' (Acc: {tag.book_item.accession_number})"
            
            # Queue high-priority security alert
            notif = Notification(
                recipient="security-ops@library.local",
                channel=NotificationChannel.EMAIL.value,
                event_type="GATE_SECURITY_ALERT",
                subject=f"CRITICAL: Unauthorized Book Removal Detected at {event_in.reader_id}",
                message_body=f"Security gate alert triggered for {item_desc}. EPC: {event_in.epc}. Time: {now.isoformat()}."
            )
            db.add(notif)

            AuditService.log_action(
                db=db,
                user_id=None,
                action="GATE_SECURITY_ALARM",
                entity_type="RFID_GATE",
                entity_id=event_in.epc,
                details={"reader_id": event_in.reader_id, "item": item_desc, "alarm": True}
            )

        db.commit()
        db.refresh(gate_event)
        return gate_event

