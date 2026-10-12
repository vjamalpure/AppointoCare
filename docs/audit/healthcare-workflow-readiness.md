# Healthcare Workflow Readiness & Gap Analysis (MVP Validation)

## Executive Summary
This document provides a verified, evidence-based assessment of the Healthcare MVP capabilities in AppointoCare (`ORG1` — City Care Health & Dental) following the implementation and verification of Milestone B security guards, the shared PDF document engine, and the Celery reminder infrastructure.

---

## 1. Scope & Verification Methodology
The analysis evaluates the existing relational models, database schema, REST API routes, frontend components, and audit controls against clinical MVP operational requirements in India (including ABDM / DISHA guidance, MCI/NMC regulations, and GST exemption norms).

- **Current Sector**: Healthcare (`ORG1`)
- **Primary Actors**: Patient, Doctor (`doc_sarah`), Clinical Staff (`staff1`), Clinic Admin (`org1`)
- **Key Models**: `Patient`, `Customer`, `User`, `Appointment`, `IndustryRecord`, `AppointmentTransaction`, `MessageLog`, `AuditLog`

---

## 2. Capability & Gap Matrix

### 2.1 Patient Registration & History
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Demographics** | Handled in `Customer` (`customers`) and `Patient` (`patients`) models with name, phone, email, gender, dob, address. | **Operational** | Dual model exists: CRM views use `customers`, while initial schema had `patients`. Standardize on single unified patient entity or synchronize customer-patient links. |
| **Medical History** | Stored in unstructured `IndustryRecord.data` (e.g. `triage` records with past conditions, vitals, allergies). | **Partial** | Lack of indexed columns for critical clinical flags: `known_allergies`, `blood_group`, `chronic_conditions`, and emergency contact. |
| **Patient Identification** | Auto-increment numeric ID. | **Partial** | Lack of unique Medical Record Number (MRN / UHID, e.g. `CCHD-2026-0042`) for clinical identification without exposing database surrogate keys. |

---

### 2.2 Doctor Availability & Conflict Prevention
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Doctor Provisioning** | Doctors provisioned via `User` table with role `"Doctor"` (`doc_sarah`). Multi-role authorization enforced. | **Operational** | Doctor's professional council registration number (MCI / State Medical Council) is not on `User` model; currently provided per prescription. |
| **Appointment Booking** | Appointments booked via `/appointments` with date, customer, doctor/staff name, and service. | **Operational** | No automated overlap / collision detection in `POST /appointments`. Overlapping bookings for the same doctor at the same slot are permitted. |
| **Working Hours & Rosters** | Relies on manual slot selection without doctor shift/roster definitions. | **Gap** | Introduce doctor schedule templates (e.g. shift start/end, slot duration, break times) to prevent booking outside available hours. |

---

### 2.3 Clinical Encounters & Notes
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **SOAP Notes Structure** | Implemented as `IndustryRecord` with `record_type="soap_note"` (`Subjective`, `Objective`, `Assessment`, `Plan`). | **Operational** | Validated in both unit tests and `test_audit.py`. |
| **Vitals & Triage** | Implemented as `IndustryRecord` with `record_type="triage"` (BP, SpO2, Heart Rate, Temp, Triage category). | **Operational** | Validated in both backend and frontend dossier modal. |
| **Encounter State Lock** | Notes can be edited/deleted by organization staff with no post-completion lock. | **Gap** | Clinical notes should have an immutable "Signed" status preventing edits after consultation concludes, satisfying clinical record retention standards. |

---

### 2.4 Prescription Lifecycle
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Rx Data Model** | `IndustryRecord` with `record_type="prescription"`. Stores diagnosis, vitals, and structured `medications` array (`medicine_name`, `dosage`, `frequency`, `duration`, `instructions`). | **Operational** | Seeded record #1 verified and fully functional. |
| **PDF Generation** | Server-side PDF engine (`pdf_service.generate_prescription_pdf`) with clinic branding, patient details, medications table, and doctor sign-off. | **Operational** | Fully implemented using ReportLab Platypus, tested with XML escaping, Unicode support, and authorization checks. |
| **Lifecycle State Machine** | Status defaults to `"Active"`. | **Partial** | Needs formal progression: `Draft` &rarr; `Issued/Signed` &rarr; `Dispensed` &rarr; `Completed`. |
| **Digital Verification** | Printable signature line with doctor metadata. | **Operational** | Includes disclaimer: "Computer generated medical prescription. Valid with registered practitioner's physical or digital signature." |

---

### 2.5 Secure Document Storage & Downloads
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Dynamic Generation** | PDFs generated on-the-fly in-memory (BytesIO) and streamed directly to authorized callers. | **Operational** | Private health documents are never stored on public S3 buckets or static web directories. |
| **Authorization Guard** | `download_record_pdf` verifies JWT role and enforces `record.organization_id == get_organization_id()`. | **Operational** | Cross-tenant attempts return HTTP 403 (verified by `test_pdf_service.py`). |
| **Diagnostic File Uploads** | Lab reports currently store JSON metadata; file attachments not yet wired to dedicated object storage. | **Gap** | Add tenant-scoped encrypted attachment storage (local disk vault or S3 with pre-signed ephemeral URLs) for scanned radiology/lab PDFs. |

---

### 2.6 OPD Queue Management
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Token Generation** | `POST /api/v1/industry-suite/queue/create` issues sequential OPD tokens (`OPD-001`, `OPD-002`) linked to appointments. | **Operational** | Auto-increments per organization per day. |
| **Queue Advancement** | `POST /api/v1/industry-suite/queue/advance` transitions tokens (`Waiting` &rarr; `In Consultation` &rarr; `Completed` &rarr; `Skipped`). | **Operational** | Working on backend and frontend queue board. |
| **Public Waiting Display** | Frontend Queue Board requires authenticated staff login. | **Gap** | Add public/kiosk display route (`/display/queue`) showing only token numbers and patient initials (privacy-safe, no medical records exposed) for waiting room TVs. |

---

### 2.7 Billing & Receipts
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Appointment Transactions** | `AppointmentTransaction` records payments, payment methods (UPI, Cash, Card), and status. | **Operational** | Linked to appointments and organizations. |
| **Invoice / Receipt PDF** | `pdf_service.generate_invoice_pdf` and `GET /transactions/<id>/download-pdf` provide branded receipts. | **Operational** | Calculates subtotal, tax rate, and net total. |
| **GST Healthcare Exemption** | Under Indian GST (Notification 12/2017-CT Rate), healthcare services by clinical establishments are exempt (NIL rate). Cosmetic/retail items attract 18%. | **Operational** | The PDF engine now supports specifying tax exemption notes or explicit rates instead of hardcoding 18% GST across all services. |
| **Catalog Tax Flag** | `Service` model has `price` but lacks `is_tax_exempt` and `sac_code`. | **Partial** | Add optional `tax_exempt` boolean on `Service` model in a future migration so clinic invoices auto-calculate zero tax for clinical consultations. |

---

### 2.8 Appointment Notifications
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Reminder Task** | Celery task `appointment_reminder` with idempotency guard via `MessageLog(related_appointment_id)`. | **Operational** | Tested with unit tests (`test_reminders.py`). Skips cancelled/completed appointments. |
| **Batch Dispatch** | `dispatch_due_appointment_reminders(hours_ahead=24)` searches upcoming bookings and triggers reminders. | **Operational** | Idempotent: checks for prior dispatch before sending. |
| **Clinical Privacy** | Notification message contains date, time, clinic name, and doctor name. Excludes diagnosis, symptoms, or medications. | **Operational** | Prevents PHI leaks via lock-screen notifications. |
| **WhatsApp Templates** | Production Meta Cloud API requires approved template names (HSM) for business-initiated chats outside 24h. | **Partial** | Production deployment must register template `appointment_reminder_v1` on Meta WhatsApp Business Manager. |

---

### 2.9 Clinical Authorization & Audit Trails
| Dimension | Current Implementation | Status | Gap & Proposed Solution |
| :--- | :--- | :--- | :--- |
| **Role-Based Access** | `@require_roles` restricts endpoints to clinical roles (`Doctor`, `Staff`, `Admin`). | **Operational** | Doctor accounts cannot access admin billing without authorization. |
| **Tenant Isolation** | All queries scoped to `organization_id` derived from JWT claims. | **Operational** | Milestone B removed tenant-1 fallbacks and verified 400/403 rejections. |
| **Audit Logging Model** | `AuditLog` table stores `action`, `user_id`, `user_role`, `entity`, `entity_id`, and `ip_address`. | **Operational** | Table in place. Recommended next step: hook `AuditLog.log_event` to clinical document access and prescription downloads for full compliance. |

---

## 3. Prioritized Healthcare Action Plan (Post-Sprint)
1. **Immediate (No Migration Needed)**:
   - Add appointment overlap check in `appointments.py` to prevent booking conflicting slots for the same practitioner.
   - Hook `AuditLog` into PDF download routes to log every document retrieval.
2. **Next Minor Migration**:
   - Add `doctor_reg_no` and `specialization` to `User`.
   - Add `is_tax_exempt` and `hsn_sac_code` to `Service`.
   - Add `uhid` (Unique Health Identifier) to `Customer`.
