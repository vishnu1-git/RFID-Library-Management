# LibraSync: Technical Evaluation & Interview Defense Guide

**Purpose**: High-confidence preparation cheat sheet for the AISYS technical interview to secure the direct offer letter.  
**Platform**: LibraSync (Intelligent RFID-Enabled ILMS)  
**Governing Standard**: AISYS Candidate Software Development SOP  

---

## 1. The 2-Minute Opening Pitch (Memorize / Read Naturally)

> *"Good morning / afternoon. Thank you for the opportunity to present **LibraSync**.*  
>  
> *When reviewing the AISYS Software Development SOP, I identified the single most critical engineering requirement on pages 1 and 3: **the platform must never directly modify, delete, or corrupt existing institutional ILMS records**.*  
>  
> *To solve this cleanly, I designed LibraSync as a **7-layer Modular Monolith** with an independent operational database and decoupled protocol boundaries. We interface with legacy systems strictly through **NCIP 2.0** and **3M SIP2** protocol adapters without executing a single raw SQL query against legacy tables.*  
>  
> *On the hardware side, I avoided proprietary vendor SDK lock-in by establishing an abstract **device-neutral RFID middleware layer** that normalizes signals from near-field staff counter pads, handheld mobile inventory wands, 3D perimeter security gates, and contactless 13.56 MHz smart cards.*  
>  
> *For data safety, our **4-stage staging migration pipeline** isolates raw spreadsheets, quarantines intra-batch and active database duplicate collisions with exact row numbers, and provides atomic transactional rollback.*  
>  
> *Finally, our automated test suite validates **100% of the Priority Acceptance Criteria (AC 01 through AC 10)** with 15 passing Pytest test suites. Both the backend and frontend are running live, and I am excited to walk you through the architecture, code, and live demonstration."*

---

## 2. Fast Codebase Navigation Map (Where to Click on Screen)

When an evaluator asks *"Show me in the code where X is handled"*, immediately navigate to these exact files:

| Evaluator Question | Exact File to Open | Key Function / Class |
| :--- | :--- | :--- |
| **"Where do you isolate the legacy ILMS?"** | [`backend/app/integrations/ilms/base.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/integrations/ilms/base.py)<br>[`ncip_adapter.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/integrations/ilms/ncip_adapter.py) | `ILMSAdapter` ABC, `NCIP2Adapter.item_checked_out()` |
| **"Where does checkout disarm the RFID tag?"** | [`backend/app/services/circulation_service.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/services/circulation_service.py) | `CirculationService.checkout()` lines 30–65 (`tag.security_bit = False`) |
| **"Where are reference books & blocked patrons rejected?"** | [`backend/app/services/circulation_service.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/services/circulation_service.py) | `CirculationService.checkout()` lines 38–48 (HTTP 400 checks) |
| **"Where does duplicate detection happen during migration?"** | [`backend/app/services/migration_service.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/services/migration_service.py)<br>[`migration/duplicate_detector.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/migration/duplicate_detector.py) | `detect_batch_duplicates()`, `validate_job()` |
| **"Where is the atomic migration rollback?"** | [`backend/app/services/migration_service.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/services/migration_service.py)<br>[`migration/rollback.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/migration/rollback.py) | `rollback_job()` lines 120–160 |
| **"Where does the security gate handle offline mode?"** | [`rfid-middleware/adapters/security_gate.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/rfid-middleware/adapters/security_gate.py) | `offline_security_cache`, `scan_portal_passage()` |
| **"Where is contactless smart-card staff authentication?"** | [`backend/app/api/v1/auth.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/api/v1/auth.py)<br>[`backend/app/core/permissions.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/core/permissions.py) | `smart_card_login()`, `get_current_active_user()` |
| **"Where are the 18 database models defined?"** | [`database/schema.sql`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/database/schema.sql)<br>[`backend/app/models/`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/backend/app/models/) | All 18 relational models & foreign keys |
| **"Where are all 10 acceptance criteria tested?"** | [`tests/acceptance/test_aisys_ac_all.py`](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/tests/acceptance/test_aisys_ac_all.py) | `test_ac01` through `test_ac10` |

---

## 3. Deep Technical Q&A Defense

### Q1: Why did you choose a Modular Monolith instead of Microservices?
- **Answer**: *"Microservices introduce distributed transactions (2-Phase Commit / Sagas), network serialization latency, and complex deployment orchestration that add fragility to a single-site library deployment. By choosing a Modular Monolith, we achieve transactional ACID consistency across circulation, inventory, and fines within PostgreSQL, with zero inter-service network overhead. However, the modules are strictly decoupled: if physical scaling requires isolating the RFID hardware listeners, the `rfid-middleware/` module can be extracted into an independent network daemon communicating via outbox queues with zero modifications to application domain services."*

### Q2: How did you ensure the legacy ILMS database is 100% protected against corruption?
- **Answer**: *"We enforced a strict zero-touch isolation policy. LibraSync maintains its own operational database (`librasync`). No connection string, ORM model, or SQL query in LibraSync has write access to the external legacy database. Inter-system communication is exclusively mediated via documented protocol adapters implementing **NCIP 2.0** (`ItemCheckedOut`, `ItemCheckedIn`) and **3M SIP2** protocol packets. If the external legacy host is offline, LibraSync serves requests seamlessly from its local operational cache."*

### Q3: What RFID standards did you use and how is the 96-bit Gen 2 memory partitioned?
- **Answer**: *"We adhere to **EPC Class 1 Gen 2 (ISO 18000-6C)** and **ISO 28560** (RFID in libraries). Tags are encoded as 24-character hexadecimal strings (96 bits) partitioned into:
  - Header: 8 bits
  - Filter Bit / Material Type: 3 bits (Book, Media, Equipment)
  - Partition: 3 bits
  - Institution Code: 24 bits
  - Item Accession ID: 38 bits
  - Serial Copy Number: 20 bits  
  The EAS (Electronic Article Surveillance) security bit is toggled dynamically: Armed (`True`) when in stacks or checked in, and Disarmed (`False`) when issued at the circulation desk."*

### Q4: How does the security gate function if the campus network drops (AC 09)?
- **Answer**: *"The gate middleware maintains an in-memory **Local Security State Cache** (`offline_security_cache`) synchronized periodically with active tag states. When a network dropout is detected, the gate makes sub-millisecond local authorization decisions: disarmed tags pass freely, while armed tags trigger local audible and visual perimeter sirens with zero server latency. All passage events are buffered in an `offline_event_queue` and replayed to the server once connectivity is restored."*

### Q5: How do you handle duplicate records during spreadsheet migrations (AC 01)?
- **Answer**: *"We use a staging-first architecture. Uploaded workbooks are first written into an isolated `migration_staging` buffer. Our duplicate detector executes two checks:
  1. **Intra-batch collisions**: Detects repeated ISBNs or Member Codes within the uploaded file itself.
  2. **Operational DB collisions**: Queries existing production tables (`books` and `members`) for conflicting unique keys.  
  Offending records are quarantined into `migration_errors` with row numbers and failure reasons, while clean records are committed to production in an atomic ACID transaction."*

### Q6: How does your disaster recovery rollback work (AC 10)?
- **Answer**: *"Every committed migration job tracks the exact batch `job_id`. If an administrative error is discovered, the rollback engine deletes all operational records created by that `job_id` inside a single atomic transaction. Crucially, the rollback action itself is recorded in our append-only `audit_logs` table, ensuring an untampered audit trail."*

### Q7: Why did you use Argon2id for password hashing instead of bcrypt or PBKDF2?
- **Answer**: *"Argon2id is the winner of the Password Hashing Competition (RFC 9106) and the gold standard recommended by OWASP. Unlike bcrypt (which has a 72-byte truncation limit) and PBKDF2 (which is vulnerable to GPU-accelerated parallel brute-forcing), Argon2id provides memory-hardness. We configured it with a memory cost of 64 MB (65,536 KiB), 2 iterations, and 2 parallel threads, making hardware-accelerated attacks computationally prohibitive."*

---

## 4. Live Demonstration Walkthrough Script (5-Minute Winning Demo)

1. **Dashboard (`/`)**: Show the 8 KPI cards, Recharts velocity chart, and live audit feed.
2. **Staff Login (`/login`)**: Demonstrate the simulated **Contactless Smart Card Reader**. Click **Tap Admin Smart Card** (`CARD-STAFF-ADMIN-01`) to show zero-password instantaneous role resolution.
3. **Circulation Presets (`/circulation`)**:
   - Click **Test AC 04: Reference Only**: Show the instant HTTP 400 rejection banner blocking reference volume loans.
   - Click **Test AC 04: Blocked Member**: Show the instant loan rejection for delinquent patrons with unpaid fines.
   - Run a normal checkout: Show the RFID tag security bit toggle from Armed (`True`) to Disarmed (`False`).
4. **Handheld Inventory (`/inventory`)**: Select shelf `SHELF-COM-01` and click **Simulate Rapid Shelf Sweep**. Show the amber badge highlighting a misplaced Architecture volume on Computer Science stacks.
5. **Security Gates (`/gates`)**: Click **Simulate Armed Tag Exit**. Watch the perimeter warning siren activate, accompanied by an optical CCTV snapshot preview and security log entry.
6. **Data Migration (`/migration`)**: Upload `sample-data/books.xlsx`. Show clean staging, duplicate collision quarantine, atomic operational commit, and one-click rollback.
7. **Terminal**: Run `pytest tests/ -v` to show **15 passed in under 3 seconds**.

You are 100% prepared to ace the technical evaluation and secure the offer letter!
