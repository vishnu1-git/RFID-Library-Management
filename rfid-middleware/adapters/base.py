from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import datetime


class RFIDEvent:
    def __init__(
        self,
        event_id: str,
        reader_id: str,
        event_type: str,
        epc: str,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.event_id = event_id
        self.reader_id = reader_id
        self.event_type = event_type
        self.epc = epc
        self.timestamp = timestamp or datetime.datetime.utcnow().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "reader_id": self.reader_id,
            "event_type": self.event_type,
            "epc": self.epc,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class RFIDReader(ABC):
    """Common abstraction for all physical and simulated RFID hardware (AISYS SOP page 4)."""

    def __init__(self, reader_id: str, location: str):
        self.reader_id = reader_id
        self.location = location
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establishes device serial, USB, or TCP connection."""
        pass

    @abstractmethod
    def read_tags(self) -> List[RFIDEvent]:
        """Polls or awaits RFID EPC tags in reader RF field."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Closes hardware interface cleanly."""
        pass

