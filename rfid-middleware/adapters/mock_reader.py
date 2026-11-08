import uuid
import random
from typing import List
from .base import RFIDReader, RFIDEvent


class MockUniversalReader(RFIDReader):
    """Configurable synthetic RFID simulator for automated testing and test-bench evaluation."""

    def __init__(self, reader_id: str = "MOCK-GENERIC-01", location: str = "Test Bench"):
        super().__init__(reader_id, location)
        self.preset_tags: List[str] = [
            "E20034120123456789010001",
            "E20034120123456789010002",
            "E20034120123456789010003"
        ]

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def read_tags(self) -> List[RFIDEvent]:
        if not self.preset_tags:
            return []
        selected = random.choice(self.preset_tags)
        return [
            RFIDEvent(
                event_id=f"mock-{uuid.uuid4().hex[:8]}",
                reader_id=self.reader_id,
                event_type="TAG_DETECTED",
                epc=selected,
                metadata={"mock": True}
            )
        ]

    def disconnect(self) -> bool:
        self.is_connected = False
        return True
