import json
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, OutboxEvent


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        details: Optional[Any] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        details_str = json.dumps(details) if isinstance(details, (dict, list)) else str(details or "")
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            details=details_str,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @staticmethod
    def queue_outbox_event(
        db: Session,
        event_type: str,
        payload: dict
    ) -> OutboxEvent:
        event = OutboxEvent(
            event_type=event_type,
            payload=json.dumps(payload),
            status="PENDING"
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

