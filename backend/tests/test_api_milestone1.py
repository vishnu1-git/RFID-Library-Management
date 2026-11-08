import pytest
from fastapi.testclient import TestClient
from app.main import app, seed_initial_data
from app.db.base import Base
from app.db.session import engine

# Ensure schema exists and seed data is populated
Base.metadata.create_all(bind=engine)
seed_initial_data()

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data


def test_admin_login():
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert "Admin" in data["user"]["roles"]


def test_smartcard_login():
    response = client.post(
        "/api/v1/auth/smartcard-login",
        json={"smart_card_uid": "CARD-STAFF-ADMIN-01"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"


def test_catalog_and_member_seeding():
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify books
    books_res = client.get("/api/v1/books", headers=headers)
    assert books_res.status_code == 200
    books = books_res.json()
    assert len(books) >= 4

    # Verify members
    members_res = client.get("/api/v1/members", headers=headers)
    assert members_res.status_code == 200
    members = members_res.json()
    assert len(members) >= 3


def test_ac04_reference_book_restriction():
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Reference book accession number: ACC-4532-01
    checkout_res = client.post(
        "/api/v1/circulation/checkout",
        json={"accession_number": "ACC-4532-01", "member_code": "MEM-2026-001"},
        headers=headers
    )
    assert checkout_res.status_code == 400
    assert "REFERENCE ONLY" in checkout_res.json()["detail"]


def test_ac04_blocked_member_restriction():
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Clean Code copy: ACC-0884-01, Blocked Member: MEM-2026-003
    checkout_res = client.post(
        "/api/v1/circulation/checkout",
        json={"accession_number": "ACC-0884-01", "member_code": "MEM-2026-003"},
        headers=headers
    )
    assert checkout_res.status_code == 400
    assert "BLOCKED" in checkout_res.json()["detail"]


def test_circulation_and_rfid_security_gate_lifecycle():
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    tag_epc = "E20034120123456789010001"

    # 1. Gate scan BEFORE checkout: book is in library (security_bit == True), ALARM triggers!
    pre_gate_res = client.post(
        "/api/v1/gates/events",
        json={"reader_id": "GATE-MAIN-01", "epc": tag_epc}
    )
    assert pre_gate_res.status_code == 200
    gate_data = pre_gate_res.json()
    assert gate_data["alarm_triggered"] is True
    assert gate_data["is_authorized"] is False
    assert gate_data["cctv_snapshot_url"] is not None

    # 2. Librarian performs Checkout with RFID tag
    checkout_res = client.post(
        "/api/v1/circulation/checkout",
        json={"epc": tag_epc, "member_code": "MEM-2026-001"},
        headers=headers
    )
    assert checkout_res.status_code == 200
    circ = checkout_res.json()
    assert circ["status"] == "ISSUED"

    # 3. Gate scan AFTER checkout: book is disarmed, SILENT/AUTHORIZED passage!
    post_gate_res = client.post(
        "/api/v1/gates/events",
        json={"reader_id": "GATE-MAIN-01", "epc": tag_epc}
    )
    assert post_gate_res.status_code == 200
    post_gate_data = post_gate_res.json()
    assert post_gate_data["alarm_triggered"] is False
    assert post_gate_data["is_authorized"] is True

    # 4. Checkin book
    checkin_res = client.post(
        "/api/v1/circulation/checkin",
        json={"epc": tag_epc},
        headers=headers
    )
    assert checkin_res.status_code == 200
    assert checkin_res.json()["status"] == "RETURNED"

    # 5. After checkin, tag is re-armed (security_bit == True)
    rearm_gate_res = client.post(
        "/api/v1/gates/events",
        json={"reader_id": "GATE-MAIN-01", "epc": tag_epc}
    )
    assert rearm_gate_res.status_code == 200
    assert rearm_gate_res.json()["alarm_triggered"] is True
