# LibraSync - Intelligent RFID-Enabled Library Management System

**LibraSync** is an enterprise-grade, modular-monolith Integrated Library Management System (ILMS) with device-neutral RFID middleware, offline resilience, and strict protection for legacy institutional databases.

Designed and engineered to satisfy AISYS Candidate Software Development SOP technical evaluation criteria.

---

## 🏛️ Core Architectural Decision

> **Core Engineering Principle (AISYS SOP Pages 1 & 3):**  
> *The system must never directly modify or corrupt the existing ILMS database.*  
> LibraSync maintains its own operational database and communicates with the legacy ILMS exclusively through documented interfaces (`NCIP 2.0`, `SIP2`, and device adapters).

```
[ PRESENTATION LAYER ]
  React 19 + TypeScript · Tailwind CSS · Recharts · Lucide Icons
          ↓
[ API & SECURITY LAYER ]
  FastAPI · Signed JWT · Argon2 Hashing · Role-Based Access Control (Admin/Librarian/Operator)
          ↓
[ APPLICATION SERVICES ]
  Cataloguing · Members · Circulation · Fines · RFID Tagging · Inventory · Gate Events · Migration
          ↓
[ INTEGRATION & MIDDLEWARE LAYER ]
  Staff Reader · Handheld Simulator · Security Gate (Offline-Ready) · Smart Card · NCIP · SIP2
          ↓
[ OPERATIONAL DATABASE ]
  PostgreSQL 16 (Primary) / SQLite (Zero-friction local dev fallback) · Audit Trail · Staging
```

---

## 🎯 AISYS Acceptance Criteria (AC 01 - AC 10) Matrix

| AISYS Scenario | Implementation & Verification in LibraSync | Verified Status |
| :--- | :--- | :---: |
| **AC 01 – Spreadsheet Migration** | Staging buffer (`migration_staging`), duplicate detection against batch & operational DB, row-by-row error logging. | ✅ Passed (Pytest) |
| **AC 02 – RFID Tagging** | UHF Gen 2 24-character EPC encoding, 1-to-1 unique copy association, EAS security bit management. | ✅ Passed (Pytest) |
| **AC 03 – Circulation** | Complete issue/renewal/return lifecycle with automatic RFID security bit arm/disarm. | ✅ Passed (Pytest) |
| **AC 04 – Restrictions** | Reference-only restrictions (`is_reference_only`), blocked member enforcement (`status == BLOCKED`), and loan limits. | ✅ Passed (Pytest) |
| **AC 05 – Inventory** | Handheld RFID reader simulator, shelf scanning, missing copies detection, and misplaced volume flags. | ✅ Passed (Pytest) |
| **AC 06 – Security Gate** | 3D EAS perimeter gate, unauthorized walk alarm trigger, optical CCTV snapshot simulation, and email alert dispatch. | ✅ Passed (Pytest) |
| **AC 07 – Smart-Card Login** | Contactless staff smart card reader (`X-Smartcard-UID`), zero-password fast login with granular RBAC permissions. | ✅ Passed (Pytest) |
| **AC 08 – Reports** | Filterable operational analytics, weekly circulation velocity charts, and CSV dataset export. | ✅ Passed (Pytest) |
| **AC 09 – Offline Update** | Gate offline cache (`cached_security_state`), local outbox queue, and standalone offline-runnable package. | ✅ Passed (Pytest) |
| **AC 10 – Recovery** | Database snapshot dumps (`database/schema.sql`), atomic migration rollback, and disaster recovery plan. | ✅ Passed (Pytest) |

---

## 📚 Technical Documentation & Deliverables

All system documentation and evaluation materials are indexed below:

1. [Architecture Documentation](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/architecture.md): 7-layer modular monolith, sequence diagrams, and technology rationales.
2. [Database Design & Schema](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/database-design.md): Entity-Relationship diagram, dictionary for 18 relational tables, and cascade constraints.
3. [REST API Documentation](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/api-documentation.md): Endpoints, JSON request/response contracts, and role-based access rules.
4. [Security Architecture](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/security.md): Argon2id hashing, Bearer JWT claims, contactless card authentication, and physical RFID perimeter safety.
5. [Staff & Admin User Guide](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/user-guide.md): Operational instructions for cataloging, circulation, audits, security alarms, and data migration.
6. [Test Execution & QA Report](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/test-report.md): Formal test execution summary certifying 100% pass rate (15/15 tests).
7. [Requirements Traceability Matrix (Markdown)](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/traceability-matrix.md): Mapping SOP specifications to exact files and test cases.
8. [Requirements Traceability Matrix (Excel)](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/traceability-matrix.xlsx): Formal spreadsheet matrix.
9. [Deployment & Operations Guide](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/documentation/deployment-guide.md): Docker Compose, backup/restore, and rollback procedures.
10. [Technical Presentation Deck](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/presentation/technical_presentation.md): Slide-by-slide engineering defense.
11. [Interactive HTML Slide Deck](file:///c:/Users/VISHNU/Desktop/AISYS/LibraSync/presentation/index.html): Interactive browser presentation.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.11 or 3.12
- **Node.js**: v20+ or v24+
- **Docker Desktop** *(Optional for PostgreSQL 16 container)*

### 2. Run Backend
```powershell
cd LibraSync/backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Run Frontend
```powershell
cd LibraSync/frontend
npm run dev
```
- Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🔑 Default Credentials & Simulated Smart Cards

| Role | Username | Password | Smart Card UID (One-Click Tap) |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `adminpassword123` | `CARD-STAFF-ADMIN-01` |
| **Chief Librarian** | `librarian` | `librarianpassword123` | `CARD-STAFF-LIB-01` |

---

## 🧪 Automated Test Execution

Execute the master acceptance test suite covering AC 01 to AC 10:
```powershell
cd LibraSync
.\backend\venv\Scripts\python.exe -m pytest tests/ -v
```

---

## 🐳 Docker Deployment
When Docker Desktop is running:
```powershell
cd LibraSync
docker compose up -d
```
All services (PostgreSQL 16, FastAPI backend, and Nginx-served React frontend) will spin up automatically.
