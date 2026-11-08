from typing import Dict, Any
from app.integrations.ilms.base import ILMSAdapter


class NCIPAdapter(ILMSAdapter):
    """
    NISO Circulation Protocol (NCIP 2.0) Adapter.
    Translates circulation events into standard XML/JSON NCIP message payloads.
    """

    def __init__(self, endpoint_url: str = "http://ilms.local:8080/ncip"):
        self.endpoint_url = endpoint_url

    def lookup_item(self, item_id: str) -> Dict[str, Any]:
        # Formats NCIP LookupItem message contract
        return {
            "protocol": "NCIP_2_0",
            "message": "LookupItemResponse",
            "item_id": item_id,
            "status": "CIRCULATING"
        }

    def lookup_patron(self, patron_id: str) -> Dict[str, Any]:
        return {
            "protocol": "NCIP_2_0",
            "message": "LookupUserResponse",
            "user_id": patron_id,
            "status": "ACTIVE"
        }

    def checkout_item(self, item_id: str, patron_id: str) -> Dict[str, Any]:
        return {
            "protocol": "NCIP_2_0",
            "message": "CheckOutItemResponse",
            "item_id": item_id,
            "user_id": patron_id,
            "transaction_status": "SUCCESS"
        }

    def checkin_item(self, item_id: str) -> Dict[str, Any]:
        return {
            "protocol": "NCIP_2_0",
            "message": "CheckInItemResponse",
            "item_id": item_id,
            "transaction_status": "SUCCESS"
        }
