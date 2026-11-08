# LibraSync REST API Specification

LibraSync exposes typed REST APIs rooted at `/api/v1` with automatic interactive OpenAPI documentation at `http://localhost:8000/docs`.

---

## 1. Authentication & Security

### `POST /api/v1/auth/login`
Authenticates staff members using username and password.
* **Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
* **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@librasync.edu",
    "username": "admin",
    "full_name": "System Administrator",
    "is_active": true,
    "roles": ["Admin"]
  }
}
```

### `POST /api/v1/auth/smartcard-login` (AC 07)
Authenticates staff members using a simulated contactless smart card UID.
* **Request Body**:
```json
{
  "smart_card_uid": "CARD-STAFF-ADMIN-01"
}
```

---

## 2. Circulation & Policy Restrictions (AC 03 & AC 04)

### `POST /api/v1/circulation/checkout`
Issues a physical book copy to an active library member.
* **Request Body**:
```json
{
  "member_code": "MEM-2026-001",
  "epc": "E20034120123456789010001"
}
```
* **Validation Rules**:
  * Returns `400 Bad Request` if book is marked `is_reference_only: true`.
  * Returns `400 Bad Request` if member status is `BLOCKED`.
  * Returns `400 Bad Request` if member outstanding fines exceed `$100.00`.
  * Returns `400 Bad Request` if book copy is already `ISSUED`.

### `POST /api/v1/circulation/checkin`
Returns a checked-out book and automatically re-arms the RFID security bit.
* **Request Body**:
```json
{
  "epc": "E20034120123456789010001"
}
```

---

## 3. Security Perimeter Gates (AC 06)

### `POST /api/v1/gates/events`
Ingests an RFID detection event from a security gate reader.
* **Request Body**:
```json
{
  "reader_id": "GATE-NORTH-EXIT-01",
  "epc": "E20034120123456789010001"
}
```
* **Response**:
  * If tag is **ARMED**: `alarm_triggered: true`, `is_authorized: false`, includes simulated optical `cctv_snapshot_url`.
  * If tag is **DISARMED**: `alarm_triggered: false`, `is_authorized: true`.

---

## 4. Handheld RFID Inventory (AC 05)

### `POST /api/v1/inventory/start`
Starts a shelf-reading session.
* **Request**: `{"session_name": "Stack A Audit", "target_shelf": "SHELF-COM-01"}`

### `POST /api/v1/inventory/scan`
Records a handheld reader tag read.
* **Request**: `{"session_id": 1, "epc": "E20034120123456789010007", "detected_shelf": "SHELF-COM-01"}`
* **Response**: Flags `is_misplaced: true` if the book's cataloged shelf differs from `detected_shelf`.

---

## 5. Staging-First Migration & Rollback (AC 01 & AC 10)

* `POST /api/v1/migration/upload?file_type=BOOKS`: Stages rows into `migration_staging`.
* `POST /api/v1/migration/validate/{job_id}`: Validates format and checks duplicate collisions.
* `POST /api/v1/migration/execute`: Atomically commits clean records into operational tables.
* `POST /api/v1/migration/rollback`: Atomically deletes records created by the given job.
