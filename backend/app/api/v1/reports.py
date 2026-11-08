import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.book import Book, BookItem, BookItemStatus
from app.models.member import Member
from app.models.rfid import RFIDTag
from app.models.circulation import Circulation, CirculationStatus, Fine, FineStatus
from app.models.gate import GateEvent
from app.schemas.report import DashboardStats

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    now = datetime.datetime.utcnow()
    today_start = datetime.datetime(now.year, now.month, now.day)

    total_books = db.query(Book).count()
    total_copies = db.query(BookItem).count()
    available_books = db.query(BookItem).filter(BookItem.status == BookItemStatus.AVAILABLE.value).count()
    issued_books = db.query(BookItem).filter(BookItem.status == BookItemStatus.ISSUED.value).count()
    registered_members = db.query(Member).count()
    rfid_tagged_items = db.query(RFIDTag).filter(RFIDTag.book_item_id.isnot(None)).count()
    
    active_fines_count = db.query(Fine).filter(Fine.status == FineStatus.UNPAID.value).count()
    total_unpaid = db.query(func.sum(Fine.amount)).filter(Fine.status == FineStatus.UNPAID.value).scalar() or 0.0

    today_transactions = db.query(Circulation).filter(Circulation.checkout_date >= today_start).count()
    unresolved_gate_alerts = db.query(GateEvent).filter(GateEvent.alarm_triggered == True, GateEvent.resolved == False).count()

    # Category distribution for charts
    categories_raw = db.query(Book.category, func.count(Book.id)).group_by(Book.category).all()
    category_distribution = [{"name": c[0] or "General", "value": c[1]} for c in categories_raw]

    # Daily circulation trend (last 7 days)
    daily_circulation_trend = []
    for d in range(6, -1, -1):
        day_date = today_start - datetime.timedelta(days=d)
        day_next = day_date + datetime.timedelta(days=1)
        count = db.query(Circulation).filter(Circulation.checkout_date >= day_date, Circulation.checkout_date < day_next).count()
        daily_circulation_trend.append({"day": day_date.strftime("%a"), "checkouts": count})

    # Recent transactions
    recent_circs = db.query(Circulation).order_by(Circulation.id.desc()).limit(5).all()
    recent_transactions = [
        {
            "id": c.id,
            "book_title": c.book_item.book.title if c.book_item else "Unknown",
            "member_name": c.member.full_name if c.member else "Unknown",
            "date": c.checkout_date.strftime("%Y-%m-%d %H:%M"),
            "status": c.status
        }
        for c in recent_circs
    ]

    return DashboardStats(
        total_books=total_copies or total_books,
        available_books=available_books,
        issued_books=issued_books,
        registered_members=registered_members,
        rfid_tagged_items=rfid_tagged_items,
        active_fines_count=active_fines_count,
        total_unpaid_fines=round(float(total_unpaid), 2),
        today_transactions_count=today_transactions,
        unresolved_gate_alerts_count=unresolved_gate_alerts,
        recent_transactions=recent_transactions,
        category_distribution=category_distribution,
        daily_circulation_trend=daily_circulation_trend
    )

