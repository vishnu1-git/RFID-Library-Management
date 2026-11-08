from typing import Dict, Any
from app.integrations.ilms.base import ILMSAdapter


class MockILMS(ILMSAdapter):
    """
    Simulated external ILMS service.
    Guarantees isolation of the external legacy database while validating interface behavior.
    """

    def lookup_item(self, item_id: str) -> Dict[str, Any]:
        return {"item_id": item_id, "exists": True, "ilms_source": "Legacy-Koha-Mock"}

    def lookup_patron(self, patron_id: str) -> Dict[str, Any]:
        return {"patron_id": patron_id, "standing": "GOOD", "fines": 0.0}

    def checkout_item(self, item_id: str, patron_id: str) -> Dict[str, Any]:
        return {"status": "SUCCESS", "item_id": item_id, "patron_id": patron_id, "mode": "MOCK_SYNC"}

    def checkin_item(self, item_id: str) -> Dict[str, Any]:
        return {"status": "SUCCESS", "item_id": item_id, "mode": "MOCK_SYNC"}

