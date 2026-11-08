# LibraSync Security Architecture & Threat Model

## 1. Authentication & Cryptography

### Password Hashing: Argon2id
LibraSync uses **Argon2id** (`argon2-cffi`), winner of the Password Hashing Competition (PHC), configured with:
* `memory_cost`: 65,536 KiB (64 MB)
* `time_cost`: 2 iterations
* `parallelism`: 2 threads
* `salt_len`: 16 bytes
* `hash_len`: 32 bytes

This provides robust resistance against GPU/ASIC-accelerated brute force and side-channel timing attacks.

### Token Authentication: Signed JWT
* **Algorithm**: HMAC SHA-256 (`HS256`).
* **Expiration**: Configurable (default: 12 hours).
* **Claims**: Subject (`sub`), primary role (`role`), expiration timestamp (`exp`).

---

## 2. Role-Based Access Control (RBAC) Matrix

| Endpoint / Operation | Operator | Librarian | Administrator |
| :--- | :---: | :---: | :---: |
| Issue / Return / Renew | ✅ | ✅ | ✅ |
| View Catalog & Members | ✅ | ✅ | ✅ |
| Encode / Bind RFID Tags | ❌ | ✅ | ✅ |
| Add / Edit Catalog Titles | ❌ | ✅ | ✅ |
| Register / Block Members | ❌ | ✅ | ✅ |
| Settle / Waive Fines | ❌ | ✅ | ✅ |
| Upload Migration Spreadsheet | ❌ | ❌ | ✅ |
| Execute / Rollback Migration | ❌ | ❌ | ✅ |
| Manage Staff Accounts | ❌ | ❌ | ✅ |
| Inspect Immutable Audit Trail| ❌ | ❌ | ✅ |

---

## 3. Physical RFID Perimeter Security (AC 06 & AC 09)

```
[ Library Stacks ]                   [ Security Gate Portal ]           [ Security Operations ]
Book on shelf (Tag ARMED)  ------>   Antenna detects ARMED tag   ----->  Siren Activates (Audio/Visual)
                                                 │                       Optical CCTV Snapshot Captured
                                                 │                       Email Dispatch Queued
                                                 ▼
                                     Offline Cache Fallback (AC 09):
                                     Local flash memory stores security bit;
                                     evaluates breach without backend dependency.
```

* **EAS Security Bit Automation**:
  * Tag starts **ARMED** (`security_bit: true`) inside library.
  * Checkout **DISARMS** the tag (`security_bit: false`).
  * Gate allows disarmed tag through with green visual clearance.
  * Checkin immediately **RE-ARMS** the tag (`security_bit: true`).
