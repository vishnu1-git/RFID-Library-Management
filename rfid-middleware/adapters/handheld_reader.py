import uuid
from typing import List
from .base import RFIDReader, RFIDEvent


class HandheldReader(RFIDReader):
    """Mobile pistol-grip RFID reader used for shelf verification and inventory audits (AC 05)."""

    def __init__(self, reader_id: str = "HANDHELD-GUN-01", location: str = "Stack Area"):
        super().__init__(reader_id, location)
        self.scanned_epcs: List[str] = []

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def trigger_sweep(self, epc_list: List[str]):
        self.scanned_epcs = list(epc_list)

    def read_tags(self) -> List[RFIDEvent]:
        events = []
        for epc in self.scanned_epcs:
            events.append(
                RFIDEvent(
                    event_id=f"hh-{uuid.uuid4().hex[:8]}",
                    reader_id=self.reader_id,
                    event_type="TAG_DETECTED",
                    epc=epc,
                    metadata={"battery_pct": 92, "rssi_dbm": -42}
                )
            )
        self.scanned_epcs = []
        return events

    def disconnect(self) -> bool:
        self.is_connected = False
        return True
