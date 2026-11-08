# LibraSync - Requirements Package (Deliverable D1)

**System**: LibraSync (Intelligent RFID-Enabled Library Management System)  
**Standard**: AISYS Candidate Software Development SOP (Section 7, Deliverable D1)  
**Version**: 1.0.0 (Evaluation Baseline)  

---

## 1. Assumptions & Environmental Baseline

1. **Host Infrastructure**: The software is deployed on modern 64-bit operating systems (Windows 11 / Windows Server 2022+ / Linux containerized via Docker 24+).
2. **Database Engine**: Production deployment leverages **PostgreSQL 16**. For zero-dependency single-node demonstrations, an automatic connection probe falls back to an embedded SQLite transactional database (`librasync.db`) without code changes.
3. **RFID Air Interface**: Standard EPC Class 1 Generation 2 (ISO 18000-6C) UHF tags (860–960 MHz) and ISO 14443A HF smart cards (13.56 MHz). Tag data encoding conforms to **ISO 28560** (RFID in libraries).
4. **Synthetic Data**: All names, member codes, email addresses, accession numbers, and RFID EPCs generated in seed data or sample files are 100% synthetic and contain zero personally identifiable information (PII).
5. **Hardware Decoupling**: All physical hardware interfaces (desktop pads, mobile wands, security gates, smart card readers, CCTV cameras) are mediated through abstract Python adapter boundaries (`RFIDReader` ABC), allowing live deployment against real vendor SDKs by swapping concrete adapter classes without modifying core application services.

---

## 2. Clarification & Boundary Log

| Reference | Query / Ambiguity | Resolution & Architectural Decision |
| :--- | :--- | :--- |
| **SOP Page 1, §1** | How should the system integrate with an existing ILMS without corrupting it? | **Zero-Touch External Boundary**: LibraSync maintains its own operational database (`librasync`) and treats any existing ILMS as read-only. External notifications and checkouts sync via standard **NCIP 2.0** (`ItemCheckedOut`, `ItemCheckedIn`) and **3M SIP2** protocol packets. |
| **SOP Page 2, FR 07** | How should security gate events function when the main LMS is offline? | **Autonomous Edge Gate**: The `SecurityGateReader` maintains an in-memory `offline_security_cache` of tag states, evaluates tags autonomously, triggers local alarms, and writes passage events to an offline outbox queue for synchronization upon reconnection. |
| **SOP Page 2, FR 10** | How to handle duplicate records during 20,000-record spreadsheet migrations? | **Staging-First Isolation**: Raw rows are buffered in `migration_staging`. A dual-layer duplicate detector flags intra-batch duplicates and active operational DB collisions. Collisions are quarantined into `migration_errors`, while clean rows commit inside an ACID transaction with atomic rollback capability. |
| **SOP Page 3, NFR 01** | What safeguards prevent data corruption during integration? | Pre-migration database snapshots, strict transactional isolation levels, foreign key cascade protections, and immutable `audit_logs` tracking every administrative mutation. |

---

## 3. Core Use Cases (UC 01 – UC 10)

### UC 01: Contactless Staff Smart Card Authentication
- **Actor**: Circulation Librarian / System Administrator.
- **Precondition**: Staff member holds a registered 13.56 MHz smart card (`CARD-STAFF-ADMIN-01` or `CARD-STAFF-LIB-01`).
- **Flow**:
  1. Staff taps card on desktop near-field reader.
  2. Reader transmits card UID to `/api/v1/auth/smart-card-login`.
  3. Security service resolves card UID against `users.smart_card_uid`, validates `is_active == True`, and fetches roles from `user_roles`.
  4. System issues signed Bearer JWT token with claims (`sub`, `roles`, `exp`).
  5. UI switches active session and unlocks authorized navigation routes.

### UC 02: High-Speed RFID Book Checkout (Issue)
- **Actor**: Circulation Staff and Library Patron.
- **Precondition**: Patron account is `ACTIVE`; book item is `AVAILABLE`; RFID tag is armed (`security_bit == True`).
- **Flow**:
  1. Staff scans member card (`MEM-2026-001`) and places book copy on the RFID desktop pad (`E20034120123456789010002`).
  2. Circulation service checks:
     - Member status is `ACTIVE` (not `BLOCKED` or `EXPIRED`).
     - Patron active loans do not exceed `max_borrow_limit` (4 items).
     - Patron outstanding fines do not exceed \$100.00.
     - Book `is_reference_only` flag is `False`.
  3. System creates a `circulation` record with calculated due date (14 days).
  4. Book item status updates to `ISSUED`.
  5. **RFID Security Bit Disarmed**: `rfid_tags.security_bit` is toggled to `False` (0).
  6. Transaction logged in `audit_logs` and digital receipt queued.

### UC 03: RFID Book Check-in & Automatic EAS Arming
- **Actor**: Circulation Staff / Self-Return Kiosk.
- **Precondition**: Item was previously `ISSUED`.
- **Flow**:
  1. Book is placed on return pad. Reader captures EPC.
  2. System resolves active `circulation` record.
  3. If current date > due date, system calculates fine (\$2.00/day overdue), creates record in `fines`, and increments `members.outstanding_fines`.
  4. Circulation record status updates to `RETURNED`, setting `returned_at` timestamp.
  5. Book item status updates to `AVAILABLE`.
  6. **RFID Security Bit Armed**: `rfid_tags.security_bit` is toggled to `True` (1).

### UC 04: Borrowing Restriction Enforcement (AC 04)
- **Actor**: System / Librarian.
- **Condition A (Reference Volume)**: If item belongs to a bibliographic record with `is_reference_only == True`, checkout is immediately rejected with HTTP 400 (`"Cannot checkout reference-only volume outside the library stacks"`).
- **Condition B (Blocked Member)**: If member has `status == BLOCKED` or fines > \$100, checkout is rejected with HTTP 400 (`"Member is BLOCKED due to excessive overdue fines"`).

### UC 05: Handheld RFID Shelf Sweep & Misplaced Volume Detection
- **Actor**: Cataloging / Inventory Librarian.
- **Precondition**: Handheld reader connected; audit session initialized for target shelf (e.g. `SHELF-CS-01`).
- **Flow**:
  1. Staff walks aisles sweeping the mobile RFID wand across book spines.
  2. Reader captures tag EPCs in bulk.
  3. For each detected tag:
     - System retrieves registered copy and shelf location.
     - If detected shelf == registered shelf: Tag marked `VERIFIED`.
     - If detected shelf != registered shelf: Tag marked `MISPLACED` (amber alert displaying expected shelf).
     - If tag is uncataloged: Tag marked `UNKNOWN` (red flag).
  4. Session tally updates missing items (registered on shelf but not scanned).
  5. Audit report finalized and saved to `inventory_sessions`.

### UC 06: Perimeter Security Gate & Optical CCTV Incident Capture
- **Actor**: Library Security / Automated Perimeter Gate.
- **Precondition**: Gate reader active at library exit portal (`GATE-PORTAL-01`).
- **Flow**:
  1. Patron attempts to exit carrying an unissued or reference book (`security_bit == True`).
  2. Gate reader detects armed EPC passing through portal antennas.
  3. Gate triggers audible perimeter siren and visual warning strobe (`alarm_triggered = True`).
  4. System captures optical CCTV snapshot from integrated mock camera adapter with embedded timestamp and camera coordinates.
  5. Incident record created in `gate_events` and security notification dispatched.

### UC 07: Controlled Spreadsheet Migration Pipeline
- **Actor**: System Administrator.
- **Precondition**: Valid `.xlsx` or `.csv` catalog/patron file.
- **Flow**:
  1. File uploaded via UI or CLI.
  2. System writes raw rows into `migration_staging` with status `UPLOADED`.
  3. Validation engine scans batch for format errors, intra-batch duplicate ISBNs, and collisions against existing `books` table.
  4. Errors quarantined in `migration_errors` with row numbers.
  5. Clean records committed to `books` and `book_items` in an atomic transaction.
  6. Reconciles total source vs. inserted records.

### UC 08: Atomic Migration Rollback
- **Actor**: System Administrator.
- **Flow**:
  1. Admin selects a completed migration job (`job_id`).
  2. Rollback engine identifies all records created by that specific batch.
  3. System deletes operational `book_items` and `books` records cleanly inside a single transaction.
  4. Updates `migration_jobs.status` to `ROLLED_BACK`.
  5. Full event logged to immutable `audit_logs`.

---

## 4. Comprehensive Data Dictionary (18 Relational Models)

| Table | Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `id` | Integer | PK, Auto | Unique user identifier. |
| | `email` | String(255) | Unique, Not Null | Staff corporate email address. |
| | `username` | String(100) | Unique, Not Null | Staff authentication handle. |
| | `hashed_password` | String(255) | Not Null | Argon2id cryptographically hashed password. |
| | `full_name` | String(255) | Not Null | Staff display name. |
| | `is_active` | Boolean | Default True | Account operational state. |
| | `is_superuser` | Boolean | Default False | Root administrator privileges. |
| | `smart_card_uid` | String(64) | Unique, Nullable | 13.56 MHz contactless card UID. |
| `roles` | `id` | Integer | PK, Auto | Role identifier. |
| | `name` | String(50) | Unique, Not Null | Role name (`Admin`, `Librarian`, `Operator`). |
| | `description` | Text | Nullable | Role permission explanation. |
| `user_roles` | `user_id` | Integer | FK(`users.id`), PK | User foreign key. |
| | `role_id` | Integer | FK(`roles.id`), PK | Role foreign key. |
| `members` | `id` | Integer | PK, Auto | Patron record ID. |
| | `member_code` | String(50) | Unique, Not Null | Institutional member barcode (e.g. `MEM-2026-001`). |
| | `full_name` | String(255) | Not Null | Patron name. |
| | `email` | String(255) | Unique, Not Null | Patron contact email. |
| | `status` | String(20) | Default 'ACTIVE' | `ACTIVE`, `BLOCKED`, `EXPIRED`. |
| | `max_borrow_limit`| Integer | Default 4 | Configurable active checkout quota. |
| | `outstanding_fines`| Float | Default 0.0 | Cumulative unpaid penalty amount. |
| | `card_rfid_uid` | String(64) | Unique, Nullable | Patron smart card UID. |
| `books` | `id` | Integer | PK, Auto | Bibliographic title ID. |
| | `isbn` | String(20) | Unique, Not Null | Standard ISBN-10 or ISBN-13. |
| | `title` | String(500) | Not Null | Bibliographic title. |
| | `author` | String(500) | Not Null | Author / contributor statement. |
| | `publisher` | String(255) | Nullable | Publishing house. |
| | `category` | String(100) | Default 'General' | Subject classification. |
| | `is_reference_only`| Boolean | Default False | If True, item cannot be checked out. |
| | `total_copies` | Integer | Default 1 | Total owned physical copies. |
| | `available_copies`| Integer | Default 1 | Currently uncirculated copies. |
| `book_items` | `id` | Integer | PK, Auto | Physical copy identifier. |
| | `book_id` | Integer | FK(`books.id`), Not Null | Parent title reference. |
| | `accession_number`| String(50) | Unique, Not Null | Physical barcode / accession number. |
| | `shelf_location` | String(50) | Not Null | Designated home shelf (e.g. `SHELF-CS-01`). |
| | `status` | String(20) | Default 'AVAILABLE' | `AVAILABLE`, `ISSUED`, `LOST`, `WEEDED`. |
| `rfid_tags` | `id` | Integer | PK, Auto | RFID tag database record. |
| | `epc` | String(24) | Unique, Not Null | 96-bit Gen 2 UHF 24-char hexadecimal EPC. |
| | `book_item_id` | Integer | FK(`book_items.id`), Unique | 1-to-1 physical copy binding. |
| | `security_bit` | Boolean | Default True | EAS security flag (True=Armed, False=Disarmed). |
| | `is_active` | Boolean | Default True | Physical tag state. |
| `circulation` | `id` | Integer | PK, Auto | Transaction event ID. |
| | `book_item_id` | Integer | FK(`book_items.id`), Not Null | Borrowed physical item. |
| | `member_id` | Integer | FK(`members.id`), Not Null | Borrowing patron. |
| | `issued_by_id` | Integer | FK(`users.id`), Not Null | Staff member executing checkout. |
| | `issued_at` | Timestamp | Default UTC Now | Checkout timestamp. |
| | `due_date` | Timestamp | Not Null | Scheduled return timestamp. |
| | `returned_at` | Timestamp | Nullable | Actual return timestamp. |
| | `status` | String(20) | Default 'ISSUED' | `ISSUED`, `RETURNED`, `OVERDUE`. |
| | `renewal_count` | Integer | Default 0 | Times renewed (max 2). |
| `fines` | `id` | Integer | PK, Auto | Fine penalty record. |
| | `circulation_id` | Integer | FK(`circulation.id`), Not Null| Associated circulation loan. |
| | `member_id` | Integer | FK(`members.id`), Not Null | Penalized patron. |
| | `amount` | Float | Not Null | Computed fine amount. |
| | `is_paid` | Boolean | Default False | Settlement flag. |
| `inventory_sessions` | `id` | Integer | PK, Auto | Shelf audit session. |
| | `session_name` | String(255) | Not Null | Descriptive audit name. |
| | `target_shelf` | String(50) | Not Null | Shelf location under verification. |
| | `status` | String(20) | Default 'ACTIVE' | `ACTIVE`, `COMPLETED`, `CANCELLED`. |
| | `total_scanned` | Integer | Default 0 | Number of tags interrogated. |
| | `misplaced_count` | Integer | Default 0 | Detected misplaced items count. |
| `inventory_reads` | `id` | Integer | PK, Auto | Individual tag read event in audit. |
| | `session_id` | Integer | FK(`inventory_sessions.id`) | Audit session reference. |
| | `rfid_tag_id` | Integer | FK(`rfid_tags.id`), Not Null | Scanned tag. |
| | `is_misplaced` | Boolean | Default False | Shelf mismatch flag. |
| `gate_events` | `id` | Integer | PK, Auto | Perimeter security event. |
| | `reader_id` | String(50) | Not Null | Gate identifier (e.g. `GATE-PORTAL-01`). |
| | `rfid_tag_id` | Integer | FK(`rfid_tags.id`), Nullable | Interrogated tag. |
| | `is_authorized` | Boolean | Not Null | True if disarmed; False if armed. |
| | `alarm_triggered` | Boolean | Not Null | Siren/strobe trigger state. |
| | `cctv_snapshot_url`| String(500) | Nullable | Captured CCTV frame URI. |
| `migration_jobs` | `id` | Integer | PK, Auto | Migration execution job. |
| | `filename` | String(255) | Not Null | Original spreadsheet filename. |
| | `entity_type` | String(50) | Not Null | `BOOKS` or `MEMBERS`. |
| | `status` | String(20) | Not Null | `UPLOADED`, `VALIDATED`, `COMPLETED`, `ROLLED_BACK`.|
| | `total_rows` | Integer | Default 0 | Total raw records in spreadsheet. |
| | `processed_rows`| Integer | Default 0 | Successfully imported records. |
| | `error_rows` | Integer | Default 0 | Quarantined duplicate/error records. |
| `migration_staging` | `id` | Integer | PK, Auto | Temporary staging buffer. |
| | `job_id` | Integer | FK(`migration_jobs.id`) | Staging batch job. |
| | `row_number` | Integer | Not Null | Excel spreadsheet row index. |
| | `raw_data` | JSON | Not Null | Complete unparsed row payload. |
| `migration_errors` | `id` | Integer | PK, Auto | Quarantined row log. |
| | `job_id` | Integer | FK(`migration_jobs.id`) | Migration batch job. |
| | `row_number` | Integer | Not Null | Offending spreadsheet row index. |
| | `error_reason` | String(500) | Not Null | Duplicate collision or format fault. |
| `audit_logs` | `id` | Integer | PK, Auto | Immutable audit ledger. |
| | `user_id` | Integer | FK(`users.id`), Nullable | Acting staff user. |
| | `action` | String(100) | Not Null | Verb (`LOGIN`, `CHECKOUT`, `MIGRATE_COMMIT`).|
| | `entity_type` | String(50) | Not Null | Target table entity. |
| | `details` | JSON | Nullable | Full before/after mutation diff. |
| `outbox_events` | `id` | Integer | PK, Auto | Reliable offline event queue. |
| | `event_type` | String(100) | Not Null | Inter-system sync event name. |
| | `payload` | JSON | Not Null | Event payload. |
| | `is_published` | Boolean | Default False | Synchronization acknowledgment status.|
| `notifications` | `id` | Integer | PK, Auto | Multi-channel communication queue. |
| | `recipient` | String(255) | Not Null | Email address or phone number. |
| | `channel` | String(20) | Not Null | `EMAIL`, `SMS`, `PRINT`. |
| | `subject` | String(255) | Nullable | Notification header. |
| | `status` | String(20) | Default 'QUEUED' | Dispatch status. |
