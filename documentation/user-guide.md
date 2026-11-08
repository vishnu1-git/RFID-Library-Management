# LibraSync Staff & Administrator Operations User Guide

Welcome to **LibraSync** (Intelligent RFID-Enabled Library Management System). This manual provides comprehensive operational instructions for library staff, circulation librarians, and system administrators.

---

## Table of Contents
1. [System Access & Authentication](#1-system-access--authentication)
2. [Catalog & Copy Management](#2-catalog--copy-management)
3. [Member Directory & Borrowing Rules](#3-member-directory--borrowing-rules)
4. [RFID Tag Encoding & EAS Management](#4-rfid-tag-encoding--eas-management)
5. [Circulation Operations (Issue, Return, Renew)](#5-circulation-operations)
6. [Handheld RFID Shelf Auditing](#6-handheld-rfid-shelf-auditing)
7. [Perimeter Security Gates & Loss Prevention](#7-perimeter-security-gates--loss-prevention)
8. [Data Migration & Atomic Rollback](#8-data-migration--atomic-rollback)
9. [Reports, Analytics & Audit Ledger](#9-reports-analytics--audit-ledger)
10. [Troubleshooting & Offline Resilience](#10-troubleshooting--offline-resilience)

---

## 1. System Access & Authentication

LibraSync provides dual-mode authentication: credential-based login and simulated high-speed staff smart card login (RFID 13.56 MHz ISO 14443A).

### 1.1 Logging In with Credentials
1. Navigate to `http://localhost:5173/login` in your web browser.
2. Enter your authorized staff credentials:
   - **System Administrator**: Username: `admin`, Password: `adminpassword123`
   - **Circulation Librarian**: Username: `librarian`, Password: `librarianpassword123`
3. Click **Sign In**. On successful authentication, an Argon2id-verified signed Bearer JWT is stored in memory and attached to subsequent API requests.

### 1.2 Instant Contactless Smart Card Login (Fast Desk Transfer)
For high-traffic circulation desks where librarians quickly switch shifts:
1. On the Login screen, locate the **Simulated Staff Smart Card Reader** panel.
2. Click **Tap Admin Smart Card** (`CARD-STAFF-ADMIN-01`) or **Tap Librarian Smart Card** (`CARD-STAFF-LIB-01`).
3. The system reads the UID, resolves the associated staff account and RBAC roles in `users` and `user_roles`, and logs you in instantly without typing passwords.
4. When logged in, your active smart card status is visible in the top navigation bar. You can click **Simulate Smart Card Tap** at any time to switch active operators.

### 1.3 Role-Based Access Control (RBAC) Permissions Matrix
| Role | Catalog & Circulation | RFID Tagging | Inventory Audits | Security Gates | Data Migration | Admin & User Mgmt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Admin** | Read / Write | Read / Write | Full Access | Full Access | Full Access | Full Access |
| **Librarian** | Read / Write | Read / Write | Full Access | View / Acknowledge | View Only | View Only |
| **Operator** | Read Only | Tag Reader | Run Audits | View Only | No Access | No Access |

---

## 2. Catalog & Copy Management

LibraSync separates **Bibliographic Records** (the conceptual book title, author, publisher, ISBN) from **Physical Book Items** (the individual physical copies on library shelves).

### 2.1 Searching the Catalog
1. Click **Books** in the left sidebar navigation.
2. Use the live search bar at the top to filter books instantly by title, author, ISBN, or subject category.
3. The table displays:
   - Title and Author
   - ISBN-13
   - Classification Category
   - Total Copies vs. Available Copies
   - Circulation Policy Tag (`REFERENCE ONLY` or `CIRCULATING`)

### 2.2 Adding a Bibliographic Record
1. Click the **+ Add Book** button in the top right.
2. Fill in the required metadata:
   - **ISBN**: 10 or 13-digit standard identifier (e.g. `978-0132350884`).
   - **Title**: Full bibliographic title.
   - **Author**: Primary author / contributors.
   - **Publisher**: Publishing house.
   - **Category**: Subject classification (e.g. Computer Science, Literature, Engineering).
   - **Reference Only**: Check this box if the title must never circulate outside the library reading room.
   - **Initial Copies**: Number of physical copy records (`book_items`) to automatically create.
3. Click **Save Record**. Physical accession numbers (`ACC-...`) will be auto-generated with status `AVAILABLE`.

### 2.3 Physical Copy Details
Click the **Copies** pill button on any book row to view individual physical items:
- **Accession Number**: Unique physical item barcode (e.g., `ACC-2026-0001`).
- **Shelf Location**: Target permanent shelf (e.g., `SHELF-CS-01`).
- **Item Status**: `AVAILABLE`, `ISSUED`, `RESERVED`, `LOST`, or `WEEDED`.
- **Linked RFID EPC**: 24-character hexadecimal tag identifier.

---

## 3. Member Directory & Borrowing Rules

### 3.1 Managing Patrons
1. Click **Members** in the sidebar.
2. Browse active patrons or use search to find a member by name, code (`MEM-2026-xxx`), or email.
3. The member details view shows:
   - **Member Code**: Official institutional barcode.
   - **Contact Information**: Email and phone.
   - **Borrowing Status**: `ACTIVE`, `BLOCKED`, or `EXPIRED`.
   - **Borrowing Quota**: Configured maximum active loans (default: 5 books).
   - **Outstanding Fines**: Cumulative unpaid overdue penalties.

### 3.2 Toggling Member Suspension / Block
- Click the **Block Member** / **Activate Member** action button on any patron row to immediately change status.
- **Enforcement Rule**: Any borrowing attempt by a patron with `BLOCKED` status will be rejected immediately by `CirculationService` with an HTTP 400 error.

---

## 4. RFID Tag Encoding & EAS Management

LibraSync uses standard **EPC Class 1 Gen 2 (ISO 18000-6C / ISO 28560)** 96-bit UHF RFID tags represented as 24-character hexadecimal strings.

### 4.1 Understanding the EAS (Electronic Article Surveillance) Security Bit
Every physical library RFID tag maintains a stateful security bit:
- **ARMED (`security_bit = True` / `1`)**: The book is currently in the library stacks or has been checked in. If passed through the 3D security gate portal, the alarm siren sounds and optical CCTV captures the event.
- **DISARMED (`security_bit = False` / `0`)**: The book has been legitimately checked out at a staff desk. It is authorized to pass through perimeter security gates without triggering an alarm.

### 4.2 Tagging a Physical Book Copy
1. Click **RFID Tags** in the sidebar.
2. Click **+ Encode New Tag**.
3. Select an unlinked physical copy accession number from the dropdown list.
4. Enter or generate a 24-character hex EPC (e.g., `E20034120123456789010009`).
5. Click **Encode & Link**. The tag is permanently paired with the physical copy item in the operational database and set to `ARMED` by default.

---

## 5. Circulation Operations

The Circulation Desk (`/circulation`) is the high-velocity core of the library. It supports scanning RFID tags or accession barcodes directly.

### 5.1 Checking Out (Issuing) Books
1. Click **Circulation** in the sidebar.
2. Ensure the **Check Out (Issue)** tab is active.
3. Select or scan the patron's **Member ID / Code** (e.g., `MEM-2026-001`).
4. Select or scan the physical item's **RFID EPC** or enter its **Accession Number**.
5. Click **Execute Check Out**.
6. The system executes the following validation pipeline:
   - Verifies the member exists and status is `ACTIVE`.
   - Checks member active loans against `max_borrow_limit`.
   - Confirms the book item status is `AVAILABLE`.
   - **Reference Book Check**: If `book.is_reference_only` is true, checkout is rejected.
   - Creates a transaction in `circulation` table with due date (default: 14 days).
   - Automatically sets physical item status to `ISSUED`.
   - **Disarms Tag**: Sets `rfid_tags.security_bit = False`.
   - Records an immutable audit log entry.

### 5.2 Checking In (Returning) Books
1. Click the **Check In (Return)** tab.
2. Scan the returned item's **RFID Tag EPC** or enter its **Accession Number**.
3. Click **Process Check In**.
4. The system executes:
   - Locates the active `ISSUED` circulation record.
   - Checks if the return date exceeds the due date. If overdue, computes daily fine (\$1.00/day) and records in `fines` table.
   - Marks circulation record status as `RETURNED`.
   - Re-arms the RFID security bit: sets `rfid_tags.security_bit = True`.
   - Updates physical item status to `AVAILABLE`.
   - Generates a confirmation receipt.

### 5.3 Renewing Borrowed Items
1. Click the **Renew Book** tab.
2. Enter the active **Circulation Transaction ID** or scan the item.
3. Click **Extend Due Date**.
4. The system checks renewal limits (maximum 2 renewals per loan cycle) and extends the due date by 14 calendar days.

### 5.4 One-Click Acceptance Evaluation Presets (AC 04)
To assist with rapid technical demonstrations, the Circulation screen provides one-click test buttons:
- **Test AC 04: Reference Only Restriction**: Automatically attempts to check out an encyclopedic reference volume. The screen displays the caught validation rejection: *"Cannot checkout reference-only volume outside the library."*
- **Test AC 04: Blocked Member Restriction**: Automatically attempts to check out a regular circulating item using a suspended member account. The screen displays: *"Member MEM-2026-003 is BLOCKED due to excessive overdue fines."*

---

## 6. Handheld RFID Shelf Auditing

The **Inventory** module (`/inventory`) simulates staff walking through book stacks with an ultra-high-frequency (UHF) handheld RFID wand to perform high-speed shelf verification.

### 6.1 Starting an Inventory Audit Session
1. Click **Inventory** in the sidebar.
2. Enter a **Session Name** (e.g. `Annual Science Stacks Audit`) and choose the **Target Shelf Location** (e.g., `SHELF-CS-01`).
3. Click **Start New Audit Session**. The session is recorded in `inventory_sessions` with status `ACTIVE`.

### 6.2 Performing a Sweep (Scanning Books)
1. In the **Handheld Scanner Simulator** panel, you can scan tags individually or click **Simulate Rapid Shelf Sweep**.
2. As tags are read, the system cross-references each tag's linked copy in `book_items`:
   - **On Correct Shelf**: Item matches `target_shelf`. Marked verified (green indicator).
   - **Misplaced Item Detected**: Tag belongs to a book registered on a different shelf (e.g., an Architecture book placed in Computer Science). Marked with an amber alert tag indicating expected vs detected shelf.
   - **Unrecognized Tag**: Tag is not registered in the catalog. Marked with a red flag.

### 6.3 Reconciling and Finalizing the Audit
1. The real-time tally updates **Total Scanned**, **Misplaced Count**, and **Missing Items** (items registered on this shelf that were not detected in the sweep).
2. Click **Finalize & Complete Audit**. The session record is finalized, and an audit summary report is permanently archived.

---

## 7. Perimeter Security Gates & Loss Prevention

The **Gate Events** module (`/gates`) monitors the library's physical entrance/exit portal (e.g., `GATE-PORTAL-01`).

### 7.1 Real-Time Gate Portal Behavior
- **Authorized Exit (Disarmed Tag)**: When a patron exits with a properly checked-out book (`security_bit = False`), the gate permits passage. Event status: `AUTHORIZED`.
- **Unauthorized Removal (Armed Tag Alarm)**: When an unissued or reference book (`security_bit = True`) passes the gate:
  1. The gate triggers an audible siren and flashing LED perimeter alarm (`alarm_triggered = True`).
  2. The integrated optical CCTV camera simulator captures an incident snapshot with timestamp and coordinates.
  3. A high-priority security alert is dispatched to library administration.
  4. The event is permanently logged in `gate_events`.

### 7.2 Testing Perimeter Alarms in the Portal
1. On the Gate Events screen, click **Simulate Armed Tag Exit** (using tag `E20034120123456789010003`).
2. Observe the instant red alarm banner, audio-visual indicator, captured CCTV snapshot preview, and security log entry.
3. Click **Simulate Disarmed Tag Exit** (using tag `E20034120123456789010002`). Observe the green authorization confirmation without alarm trigger.

---

## 8. Data Migration & Atomic Rollback

The **Migration** module (`/migration`) implements AISYS SOP Section 3: controlled, staging-first data ingestion from external Excel (`.xlsx`) or CSV spreadsheets.

> [!IMPORTANT]
> **Core Safety Principle**: The migration engine **never directly writes to legacy ILMS tables**. All imported records are staged in `migration_staging`, rigorously validated against schema rules and collision detectors, and only then committed to the operational database inside an atomic transaction.

### 8.1 Step-by-Step Spreadsheet Ingestion
1. Click **Migration** in the left sidebar.
2. In the **Upload Spreadsheet** card, select **Entity Type**:
   - `BOOKS`: Bibliographic titles and initial copy quantities.
   - `MEMBERS`: Patron accounts, barcodes, and contact information.
3. Click **Choose File** and select a valid Excel workbook (e.g., `sample-data/books.xlsx` or `sample-data/members.xlsx`).
4. Click **Upload & Stage Records**.
   - A new job is recorded in `migration_jobs` with status `UPLOADED`.
   - Raw rows are placed in `migration_staging`.

### 8.2 In-Memory Validation & Duplicate Detection
1. Click **Validate Staging Job**.
2. The engine executes two levels of collision detection:
   - **Intra-Batch Collisions**: Duplicate ISBNs or Member Codes appearing more than once within the uploaded spreadsheet file.
   - **Operational Database Collisions**: ISBNs or Member Codes that already exist in the active `books` or `members` tables.
3. Clean rows remain staged for commit. Conflicting or malformed rows are quarantined into `migration_errors` with specific row numbers and error descriptions.

### 8.3 Committing Migration to Operational Database
1. Review the validation summary (Total Rows, Clean Rows, Quarantine Errors).
2. Click **Execute Migration Commit**.
3. All clean staged rows are inserted into `books` and `book_items` in a single ACID transaction. The job status updates to `COMPLETED`.

### 8.4 Atomic Rollback
If an import must be undone due to administrative error:
1. Locate the completed job in the **Migration History** table.
2. Click the red **Rollback** button.
3. The engine deletes all operational records created by that specific `job_id`, clears linked items, updates job status to `ROLLED_BACK`, and logs the rollback in `audit_logs`.

---

## 9. Reports, Analytics & Audit Ledger

### 9.1 Live Analytics Dashboard
- Navigate to **Dashboard** (`/`) to view 8 real-time telemetry metrics:
  - Total Cataloged Titles & Physical Copies
  - Circulating vs. Reference Collections
  - Registered Patrons & Active Loans
  - Overdue Fines Accrual
  - Active RFID Tags & Armed Ratio
- Visual analytics generated by Recharts:
  - **7-Day Circulation Velocity**: Daily issues vs. returns.
  - **Collection Distribution by Category**: Classification breakdown.

### 9.2 Circulation Ledger & CSV Export
1. Click **Reports** in the sidebar.
2. Filter transactions by date range, transaction type (`ISSUE`, `RETURN`, `RENEW`), or patron code.
3. Click **Export to CSV** to download a standardized report for institutional reporting.

### 9.3 Immutable Audit Trail
1. Click **Admin** in the sidebar.
2. The **Audit Log Ledger** records every user action, including staff login, item checkout, manual fine adjustments, inventory sessions, and migration operations.
3. Each record contains: timestamp, staff username, action verb, target entity, record ID, and JSON change payload.

---

## 10. Troubleshooting & Offline Resilience

### 10.1 Security Gate Offline Autonomous Mode (AC 09)
If the local area network connection between the 3D perimeter gate and the backend server drops:
- The gate middleware (`SecurityGateReader`) automatically switches to **Offline Autonomous Mode**.
- It consults a **Local In-Memory Security State Cache** (`offline_security_cache`) updated during the last periodic synchronization.
- Armed tags continue to trigger physical alarms locally.
- All passage events are appended to a persistent local buffer (`offline_event_queue`) and automatically flushed to the server once network connectivity is restored.

### 10.2 Database Connection Diagnostics
- Navigate to **Settings** (`/settings`) to view live database connectivity status.
- LibraSync connects to **PostgreSQL 16** via connection pool. If Docker or PostgreSQL is not running during local evaluation, the database layer automatically activates zero-friction development fallback to **SQLite** (`backend/app/librasync.db`), ensuring zero downtime during demonstrations.
