import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_books: int
    available_books: int
    issued_books: int
    registered_members: int
    rfid_tagged_items: int
    active_fines_count: int
    total_unpaid_fines: float
    today_transactions_count: int
    unresolved_gate_alerts_count: int
    recent_transactions: List[Dict[str, Any]] = []
    category_distribution: List[Dict[str, Any]] = []
    daily_circulation_trend: List[Dict[str, Any]] = []


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime.datetime

    class Config:
        from_attributes = True
