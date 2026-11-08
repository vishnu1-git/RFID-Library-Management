import datetime
from typing import Dict, Any
from app.integrations.ilms.base import ILMSAdapter


class SIP2Adapter(ILMSAdapter):
    """
    Standard Interchange Protocol (3M SIP2) Adapter.
    Translates circulation events into SIP2 frames (11/12 Checkout, 09/10 Checkin).
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 6001):
        self.host = host
        self.port = port

    def lookup_item(self, item_id: str) -> Dict[str, Any]:
        return {
            "protocol": "SIP2",
            "frame": "17 (Item Information Request)",
            "item_id": item_id,
            "circulation_status": "AVAILABLE"
        }

    def lookup_patron(self, patron_id: str) -> Dict[str, Any]:
        return {
            "protocol": "SIP2",
            "frame": "63 (Patron Information Request)",
            "patron_id": patron_id,
            "status": "VALID"
        }

    def checkout_item(self, item_id: str, patron_id: str) -> Dict[str, Any]:
        now_str = datetime.datetime.utcnow().strftime("%Y%m%d    %H%M%S")
        return {
            "protocol": "SIP2",
            "frame": "11 (Checkout Request)",
            "raw_payload": f"11YN{now_str}AO|AA{patron_id}|AB{item_id}|",
            "ok": True
        }

    def checkin_item(self, item_id: str) -> Dict[str, Any]:
        now_str = datetime.datetime.utcnow().strftime("%Y%m%d    %H%M%S")
        return {
            "protocol": "SIP2",
            "frame": "09 (Checkin Request)",
            "raw_payload": f"09N{now_str}AO|AB{item_id}|",
            "ok": True
        }

