-- =========================================================================
-- LibraSync - Intelligent RFID-Enabled Library Management System (ILMS)
-- PostgreSQL 16 Relational Schema Definition
-- =========================================================================

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    smart_card_uid VARCHAR(64) UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    member_code VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    department VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE' NOT NULL,
    max_borrow_limit INTEGER DEFAULT 4 NOT NULL,
    outstanding_fines DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
    card_rfid_uid VARCHAR(64) UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publisher VARCHAR(255),
    publication_year INTEGER,
    category VARCHAR(100),
    description TEXT,
    is_reference_only BOOLEAN DEFAULT FALSE NOT NULL,
    total_copies INTEGER DEFAULT 1 NOT NULL,
    available_copies INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS book_items (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    accession_number VARCHAR(64) UNIQUE NOT NULL,
    barcode VARCHAR(64) UNIQUE,
    status VARCHAR(20) DEFAULT 'AVAILABLE' NOT NULL,
    shelf_location VARCHAR(64),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rfid_tags (
    id SERIAL PRIMARY KEY,
    epc VARCHAR(64) UNIQUE NOT NULL,
    tid VARCHAR(64),
    book_item_id INTEGER UNIQUE REFERENCES book_items(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    security_bit BOOLEAN DEFAULT TRUE NOT NULL,
    last_seen_at TIMESTAMP WITHOUT TIME ZONE,
    last_seen_reader VARCHAR(64),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS circulation (
    id SERIAL PRIMARY KEY,
    book_item_id INTEGER NOT NULL REFERENCES book_items(id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    issued_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    checkout_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    due_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    return_date TIMESTAMP WITHOUT TIME ZONE,
    renewal_count INTEGER DEFAULT 0 NOT NULL,
    status VARCHAR(20) DEFAULT 'ISSUED' NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS fines (
    id SERIAL PRIMARY KEY,
    circulation_id INTEGER REFERENCES circulation(id) ON DELETE SET NULL,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'UNPAID' NOT NULL,
    paid_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_sessions (
    id SERIAL PRIMARY KEY,
    session_name VARCHAR(100) NOT NULL,
    target_shelf VARCHAR(50),
    initiated_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE' NOT NULL,
    total_scanned INTEGER DEFAULT 0 NOT NULL,
    missing_count INTEGER DEFAULT 0 NOT NULL,
    misplaced_count INTEGER DEFAULT 0 NOT NULL,
    start_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    end_time TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS inventory_reads (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES inventory_sessions(id) ON DELETE CASCADE,
    epc VARCHAR(64) NOT NULL,
    book_item_id INTEGER REFERENCES book_items(id) ON DELETE SET NULL,
    detected_shelf VARCHAR(64) NOT NULL,
    expected_shelf VARCHAR(64),
    is_misplaced BOOLEAN DEFAULT FALSE NOT NULL,
    read_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS gate_events (
    id SERIAL PRIMARY KEY,
    reader_id VARCHAR(64) NOT NULL,
    epc VARCHAR(64) NOT NULL REFERENCES rfid_tags(epc) ON DELETE CASCADE,
    book_item_id INTEGER REFERENCES book_items(id) ON DELETE SET NULL,
    is_authorized BOOLEAN DEFAULT FALSE NOT NULL,
    alarm_triggered BOOLEAN DEFAULT TRUE NOT NULL,
    cctv_snapshot_url VARCHAR(255),
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved BOOLEAN DEFAULT FALSE NOT NULL,
    resolved_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    recipient VARCHAR(255) NOT NULL,
    channel VARCHAR(20) DEFAULT 'EMAIL' NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    subject VARCHAR(255),
    message_body TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'QUEUED' NOT NULL,
    sent_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(64),
    details TEXT,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS migration_jobs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    total_rows INTEGER DEFAULT 0 NOT NULL,
    processed_rows INTEGER DEFAULT 0 NOT NULL,
    error_rows INTEGER DEFAULT 0 NOT NULL,
    status VARCHAR(30) DEFAULT 'UPLOADED' NOT NULL,
    started_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS migration_staging (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES migration_jobs(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL,
    record_type VARCHAR(50) NOT NULL,
    raw_data TEXT NOT NULL,
    validation_status VARCHAR(30) DEFAULT 'PENDING' NOT NULL,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS migration_errors (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES migration_jobs(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL,
    field_name VARCHAR(100),
    error_reason TEXT NOT NULL,
    raw_record TEXT
);

CREATE TABLE IF NOT EXISTS outbox_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    payload TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' NOT NULL,
    retry_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    processed_at TIMESTAMP WITHOUT TIME ZONE
);

-- Indexes for high-throughput RFID and Gate lookups
CREATE INDEX IF NOT EXISTS idx_rfid_tags_epc ON rfid_tags(epc);
CREATE INDEX IF NOT EXISTS idx_book_items_accession ON book_items(accession_number);
CREATE INDEX IF NOT EXISTS idx_members_code ON members(member_code);
CREATE INDEX IF NOT EXISTS idx_members_card_uid ON members(card_rfid_uid);
CREATE INDEX IF NOT EXISTS idx_circulation_status ON circulation(status);
CREATE INDEX IF NOT EXISTS idx_gate_events_timestamp ON gate_events(timestamp);

