"""
Integration Test Suite: Circulation & RFID EAS Lifecycle
Verifies checkout, renewal, checkin, and EAS security bit arm/disarm transitions.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend"))
from app.db.session import SessionLocal
from app.models.book import BookItem, BookItemStatus
from app.models.rfid import RFIDTag
from app.models.circulation import Circulation, CirculationStatus
from app.schemas.circulation import CheckoutRequest, CheckinRequest, RenewRequest
from app.services.circulation_service import CirculationService


def test_complete_circulation_lifecycle():
    db = SessionLocal()
    try:
        # 1. Setup clean test item
        item = db.query(BookItem).filter(BookItem.status == BookItemStatus.AVAILABLE.value).first()
        assert item is not None, "At least one available book copy required for test"
        tag = item.rfid_tag
        assert tag is not None
        assert tag.security_bit is True, "In-library tag must be armed"

        member_code = "MEM-2026-001"

        # 2. Checkout
        checkout_req = CheckoutRequest(epc=tag.epc, member_code=member_code)
        circ = CirculationService.checkout(db, checkout_req, operator_id=1)
        assert circ.status == CirculationStatus.ISSUED.value
        assert item.status == BookItemStatus.ISSUED.value
        assert tag.security_bit is False, "Checkout must disarm tag security bit"

        # 3. Renew
        renew_req = RenewRequest(circulation_id=circ.id)
        renewed_circ = CirculationService.renew(db, renew_req, operator_id=1)
        assert renewed_circ.renewal_count == 1

        # 4. Checkin
        checkin_req = CheckinRequest(epc=tag.epc)
        returned_circ = CirculationService.checkin(db, checkin_req, operator_id=1)
        assert returned_circ.status == CirculationStatus.RETURNED.value
        assert item.status == BookItemStatus.AVAILABLE.value
        assert tag.security_bit is True, "Return must re-arm tag security bit"

    finally:
        db.close()

