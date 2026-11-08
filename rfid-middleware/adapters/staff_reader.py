import uuid
from typing import List, Optional
from .base import RFIDReader, RFIDEvent


class StaffReader(RFIDReader):
    """Near-field UHF desktop pad reader for circulation checkout and tag encoding."""

    def __init__(self, reader_id: str = "STAFF-PAD-01", location: str = "Main Circulation Desk"):
        super().__init__(reader_id, location)
        self.active_tag_queue: List[str] = []

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def place_tag_on_pad(self, epc: str):
        self.active_tag_queue.append(epc)

    def read_tags(self) -> List[RFIDEvent]:
        events = []
        while self.active_tag_queue:
            epc = self.active_tag_queue.pop(0)
            events.append(
                RFIDEvent(
                    event_id=f"pad-{uuid.uuid4().hex[:8]}",
                    reader_id=self.reader_id,
                    event_type="TAG_DETECTED",
                    epc=epc,
                    metadata={"antenna": 1, "power_dbm": 15}
                )
            )
        return events

    def disconnect(self) -> bool:
        self.is_connected = False
        return True
