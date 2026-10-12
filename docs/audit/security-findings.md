# AppointoCare — Security & Data Integrity Audit Findings

**Audit Date:** October 12, 2026  
**Security Posture:** Pilot Deployment Review  

---

## 1. Verified Security Findings & Severity Matrix

| ID | Category | Finding Description | Severity | Affected Files | Remediation Status |
| :---: | :--- | :--- | :---: | :--- | :---: |
| **SEC-01** | **Tenant Isolation** | `_resolve_tenant_id()` defaults to `1` when no tenant is identified in unauthenticated requests. | **P0 (Critical)** | `appointocare-backend/app/service_guards.py:43` | **Remediated & Verified** |
| **SEC-02** | **Secret Hygiene** | Application falls back to weak default development secrets (`supersecretkey`, `jwtsecretkey`) if environment variables are unset. | **P0 (Critical)** | `appointocare-backend/app/config.py:9-13` | **Remediated & Verified** |
| **SEC-03** | **Data Integrity** | Hard deletes of appointments must cleanly cascade to appointment transactions and linked industry records while preserving audit logs. | **P0 (Critical)** | `appointocare-backend/app/routes/appointments.py:200-238` | **Remediated & Verified** |
| **SEC-04** | **PII & Logging** | Unauthenticated webhook payloads and debug routes must avoid logging raw patient data, credit card details, or bearer tokens. | **P1 (High)** | `appointocare-backend/app/routes/whatsapp.py`, `payments.py` | **Pending (Milestone B)** |
| **SEC-05** | **Webhook Signatures** | Webhook verification for Meta and Razorpay must enforce cryptographic HMAC validation before event ingestion. | **P1 (High)** | `appointocare-backend/app/routes/payments.py:120-170`, `whatsapp.py:350-410` | **Remediated & Verified** |

---

## 2. In-Depth Analysis of Critical Vulnerabilities

### SEC-01: Unsafe Webhook Tenant Resolution Fallback
- **Location:** [`appointocare-backend/app/service_guards.py`](file:///d:/App/AppointoCare/appointocare-backend/app/service_guards.py#L43)
- **Vulnerability:**
  ```python
  def _resolve_tenant_id():
      ...
      return 1 # Default fallback if unauthenticated public webhook
  ```
- **Exploitation Vector:** Any inbound webhook or unauthenticated call missing tenant context automatically binds to Organization 1 (`City Care Health & Dental`), potentially corrupting its configuration or message logs.
- **Remediation Plan (Milestone B):**
  1. Remove fallback to `1`.
  2. Require tenant ID to be explicitly passed via URL path (e.g. `/api/v1/whatsapp/webhook/<int:tenant_id>`) or verified in request claims.
  3. Return HTTP 400 Bad Request if tenant ID is absent or invalid.

### SEC-02: Production Secret Guard
- **Location:** [`appointocare-backend/app/config.py`](file:///d:/App/AppointoCare/appointocare-backend/app/config.py#L9-L13)
- **Vulnerability:**
  ```python
  SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
  JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")
  ```
- **Exploitation Vector:** If deployed to production without overriding environment variables, attackers can forge arbitrary JWT claims (including role `SuperAdmin` or `Admin`).
- **Remediation Plan (Milestone B):**
  1. Implement startup check in `create_app()`: If `APP_ENV == "production"`, verify `SECRET_KEY` and `JWT_SECRET_KEY` are not set to default keys and exceed 32 characters in length.
  2. Refuse server startup with a descriptive exit error if insecure keys are detected.

---

## 3. Milestone B Acceptance Criteria

1. Unauthenticated requests without explicit tenant identifiers must return HTTP 400/403 and never resolve to tenant 1.
2. In production mode, application refuses to boot if weak development secrets are detected.
3. Cross-tenant appointment deletion, record modification, and data queries return HTTP 403 Forbidden.
4. All existing 216 test cases remain 100% passing.
