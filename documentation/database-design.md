# LibraSync Database Design & Relational Model

## 1. Relational Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : assigned
    ROLES ||--o{ USER_ROLES : contains
    USERS ||--o{ AUDIT_LOGS : performs
    USERS ||--o{ CIRCULATION : issues
    MEMBERS ||--o{ CIRCULATION : borrows
    MEMBERS ||--o{ FINES : incurs
    BOOKS ||--|{ BOOK_ITEMS : has
    BOOK_ITEMS ||--o| RFID_TAGS : tagged_with
    BOOK_ITEMS ||--o{ CIRCULATION : circulated
    BOOK_ITEMS ||--o{ INVENTORY_READS : detected
    RFID_TAGS ||--o{ GATE_EVENTS : detected
    INVENTORY_SESSIONS ||--o{ INVENTORY_READS : contains
    MIGRATION_JOBS ||--o{ MIGRATION_STAGING : stages
    MIGRATION_JOBS ||--o{ MIGRATION_ERRORS : records

    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_superuser
        string smart_card_uid UK
        timestamp created_at
    }

    MEMBERS {
        int id PK
        string member_code UK
        string full_name
        string email UK
        string phone
        string status
        int max_borrow_limit
        float outstanding_fines
        string card_rfid_uid UK
    }

    BOOKS {
        int id PK
        string isbn UK
        string title
        string author
        string publisher
        string category
        boolean is_reference_only
        int total_copies
        int available_copies
    }

    BOOK_ITEMS {
        int id PK
        int book_id FK
        string accession_number UK
        string barcode UK
        string status
        string shelf_location
    }

    RFID_TAGS {
        int id PK
        string epc UK
        string tid
        int book_item_id FK
        boolean is_active
        boolean security_bit
        string last_seen_reader
    }

    CIRCULATION {
        int id PK
        int book_item_id FK
        int member_id FK
        int issued_by_user_id FK
        timestamp checkout_date
        timestamp due_date
        timestamp return_date
        int renewal_count
        string status
    }
```

---

## 2. Table Catalog

| Table | Responsibility | Key Constraints |
| :--- | :--- | :--- |
| `users` | Staff credentials & smart-card identity | Unique `email`, `username`, `smart_card_uid` |
| `roles` | Staff permission levels (`Admin`, `Librarian`, `Operator`) | Unique `name` |
| `user_roles` | Role assignments | Foreign keys to `users.id` & `roles.id` |
| `members` | Library patron records & borrowing standing | Unique `member_code`, `email`, `card_rfid_uid` |
| `books` | Bibliographic title catalog | Unique `isbn` |
| `book_items` | Individual physical copies | Unique `accession_number` |
| `rfid_tags` | UHF Gen 2 RFID transponders | Unique `epc`, 1-to-1 unique `book_item_id` |
| `circulation` | Issue, renewal, and return transactions | Foreign keys to `book_items`, `members`, `users` |
| `fines` | Overdue and penalty ledger | Foreign keys to `circulation` and `members` |
| `inventory_sessions`| Audit scan sessions | Tracks initiated staff and targets |
| `inventory_reads` | Handheld antenna reads | Compares detected vs expected shelf |
| `gate_events` | Security perimeter breach events | Captures reader, EPC, alarm, and CCTV URL |
| `notifications` | Outbound email, SMS, and print slips | Queued dispatch architecture |
| `audit_logs` | Immutable operational ledger | Records operator ID, action, timestamp |
| `migration_jobs` | Spreadsheet staging jobs | Tracks state (`UPLOADED`, `VALIDATED`, `EXECUTED`) |
| `migration_staging`| Uncommitted raw spreadsheet rows | Isolated staging buffer |
| `migration_errors` | Specific row-by-row failure reasons | Preserves data integrity |
| `outbox_events` | Reliable integration event queue | Guarantees at-least-once delivery |

