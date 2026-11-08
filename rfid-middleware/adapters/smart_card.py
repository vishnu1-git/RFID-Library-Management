import uuid
from typing import List
from .base import RFIDReader, RFIDEvent


class SmartCardReader(RFIDReader):
    """High-frequency 13.56MHz Mifare / DesFire staff credential card reader (AC 07)."""

    def __init__(self, reader_id: str = "CARD-DESK-01", location: str = "Circulation Terminal"):
        super().__init__(reader_id, location)
        self.tapped_card_uid: str = ""

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def tap_card(self, uid: str):
        self.tapped_card_uid = uid

    def read_tags(self) -> List[RFIDEvent]:
        if not self.tapped_card_uid:
            return []
        uid = self.tapped_card_uid
        self.tapped_card_uid = ""
        return [
            RFIDEvent(
                event_id=f"card-{uuid.uuid4().hex[:8]}",
                reader_id=self.reader_id,
                event_type="CARD_DETECTED",
                epc=uid,
                metadata={"hf_type": "ISO14443A", "sak": "08"}
            )
        ]

    def disconnect(self) -> bool:
        self.is_connected = False
        return True
