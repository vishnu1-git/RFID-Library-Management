import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adapters.staff_reader import StaffReader
from adapters.handheld_reader import HandheldReader
from adapters.security_gate import SecurityGateReader
from adapters.smart_card import SmartCardReader
from adapters.mock_reader import MockUniversalReader

def main():
    print("====================================================")
    print(" LibraSync RFID Middleware & Device Simulator (AISYS)")
    print("====================================================")
    
    gate = SecurityGateReader("GATE-NORTH-EXIT-01", "North Entrance")
    gate.connect()
    
    # Pre-cache tag states (AC 09 offline local security status)
    gate.update_offline_cache({
        "E20034120123456789010001": True,   # Armed (In Library / Unborrowed)
        "E20034120123456789010002": False,  # Disarmed (Legitimate Checkout)
    })
    
    print("\n[Simulating Security Gate Portal Event]")
    evt1 = gate.scan_portal_passage("E20034120123456789010001")
    print("Armed tag pass result (ALARM TRIGGERED):", json.dumps(evt1, indent=2))
    
    evt2 = gate.scan_portal_passage("E20034120123456789010002")
    print("Disarmed tag pass result (AUTHORIZED PASS):", json.dumps(evt2, indent=2))
    
    gate.disconnect()
    print("\nMiddleware hardware interface disconnected cleanly.")

if __name__ == "__main__":
    main()
