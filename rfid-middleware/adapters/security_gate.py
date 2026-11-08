import uuid
import datetime
from typing import List, Dict, Optional
from .base import RFIDReader, RFIDEvent


class SecurityGateReader(RFIDReader):
    """3D EAS Portal Antenna Gate with local offline cache and outbox sync (AC 06 & AC 09)."""

    def __init__(self, reader_id: str = "GATE-MAIN-01", location: str = "Library Main Portal"):
        super().__init__(reader_id, location)
        # Local offline cache: maps epc -> security_bit (True = Armed, False = Disarmed)
        self.cached_security_state: Dict[str, bool] = {}
        self.offline_event_queue: List[Dict] = []
        self.online_mode = True

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def update_offline_cache(self, tag_states: Dict[str, bool]):
        """Synchronizes local flash memory cache with backend for offline gate operation."""
        self.cached_security_state.update(tag_states)

    def scan_portal_passage(self, epc: str) -> Dict:
        """Evaluates passing tag against cached security status."""
        is_armed = self.cached_security_state.get(epc, True)  # Defaults to armed (secure)
        alarm_triggered = is_armed
        now = datetime.datetime.utcnow().isoformat()

        event = {
            "event_id": f"gate-{uuid.uuid4().hex[:8]}",
            "reader_id": self.reader_id,
            "epc": epc,
            "is_authorized": not is_armed,
            "alarm_triggered": alarm_triggered,
            "timestamp": now,
            "offline_evaluated": not self.online_mode
        }

        # Queue event if running offline
        if not self.online_mode:
            self.offline_event_queue.append(event)

        return event

    def read_tags(self) -> List[RFIDEvent]:
        # Unsolicited gate alarms
        return []

    def flush_offline_queue(self) -> List[Dict]:
        events = list(self.offline_event_queue)
        self.offline_event_queue = []
        return events

    def disconnect(self) -> bool:
        self.is_connected = False
        return True
