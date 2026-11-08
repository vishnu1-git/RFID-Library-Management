# LibraSync Deployment & Operations Guide

## 1. System Requirements

* **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 22.04 LTS recommended)
* **Python**: 3.11 or 3.12
* **Node.js**: v20 LTS or v24
* **Database**: PostgreSQL 16 (or local SQLite fallback for dev)
* **Container Runtime**: Docker Desktop / Docker Engine 24+

---

## 2. Option A: Local Bare-Metal Execution

### Backend Setup
```powershell
cd LibraSync/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```powershell
cd LibraSync/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 3. Option B: Docker Compose Deployment

Spins up PostgreSQL 16, FastAPI backend, and Nginx-fronted React application with health checks:

```powershell
cd LibraSync
docker compose up -d
```

### Checking Container Health:
```powershell
docker compose ps
docker compose logs -f backend
```

---

## 4. Disaster Recovery & Backup Procedures (AC 10)

### Generating a PostgreSQL Snapshot:
```powershell
docker exec -t librasync-postgres pg_dump -U postgres librasync > database/backups/librasync_dump_$(Get-Date -Format 'yyyyMMdd_HHmm').sql
```

### Restoring Database from Snapshot:
```powershell
cat database/backups/librasync_dump_latest.sql | docker exec -i librasync-postgres psql -U postgres -d librasync
```

### Zero-Downtime Migration Rollback:
If an erroneous spreadsheet was imported:
```powershell
cd LibraSync
python migration/rollback.py <job_id>
```
Removes all records created by the specific job ID while leaving pre-existing catalog and circulation records untouched.

