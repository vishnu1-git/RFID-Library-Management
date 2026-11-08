from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ILMSAdapter(ABC):
    """
    Core Architectural Boundary:
    The system must never directly modify or corrupt the existing ILMS database.
    Communication with legacy ILMS occurs solely through documented protocol contracts.
    """

    @abstractmethod
    def lookup_item(self, item_id: str) -> Dict[str, Any]:
        """Queries bibliographic & circulation status without direct database mutation."""
        pass

    @abstractmethod
    def lookup_patron(self, patron_id: str) -> Dict[str, Any]:
        """Queries patron standing, block flags, and fines."""
        pass

    @abstractmethod
    def checkout_item(self, item_id: str, patron_id: str) -> Dict[str, Any]:
        """Emits standard circulation checkout command to ILMS."""
        pass

    @abstractmethod
    def checkin_item(self, item_id: str) -> Dict[str, Any]:
        """Emits standard checkin/return command to ILMS."""
        pass

