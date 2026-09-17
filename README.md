# AppointoCare — Enterprise Multi-Industry SaaS Platform

<div align="center">

![AppointoCare Platform](https://img.shields.io/badge/Platform-AppointoCare-4f46e5?style=for-the-badge&logo=shield)
![Angular](https://img.shields.io/badge/Angular_18-DD0031?style=for-the-badge&logo=angular&logoColor=white)
![Flask](https://img.shields.io/badge/Python_Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis_7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**The Intelligent Operating System for Modern Appointments, Multi-Industry CRM & Operations.**

*Engineered for Healthcare, Salon & Wellness, Finance, Insurance, Retail, Education, Legal Consulting, Real Estate, and Enterprise Services.*

</div>

---

## 📌 Table of Contents
1. [Overview](#-overview)
2. [Supported Industry Sectors](#-supported-industry-sectors)
3. [Key Platform Features](#-key-platform-features)
4. [Enterprise Integrations (Meta & Razorpay)](#-enterprise-integrations-meta--razorpay)
5. [Quick Start (Docker Setup)](#-quick-start-docker-setup)
6. [Demo Accounts & Credentials](#-demo-accounts--credentials)
7. [Core REST API Endpoints](#-core-rest-api-endpoints)
8. [Automated Verification & Testing](#-automated-verification--testing)
9. [Environment Configuration](#-environment-configuration)

---

## 🚀 Overview

**AppointoCare** is a production-ready, multi-tenant scheduling and CRM platform designed for modern service enterprises. The system dynamically adapts its terminology, custom dossier fields, WhatsApp reception bots, service catalogs, and live queue boards across **9 distinct industry sectors**.

### Tech Stack
- **Frontend**: Angular 18, Angular Material, RxJS, Responsive Design System (auto-adjusts to viewport).
- **Backend API**: Python 3.12, Flask, Flask-JWT-Extended, Flask-SQLAlchemy, Marshmallow.
- **Database**: PostgreSQL 16 (Relational schemas, JSONB support for sector dossiers, B-tree indexes).
- **Caching & Async**: Redis 7, Celery Worker for background tasks and automated messaging.
- **Containerization**: Docker Compose with automatic database provisioning and schema auto-healing.

---

## 🏢 Supported Industry Sectors

| Sector | Organization Code | Default Admin | Specialist Role | Specialized Capabilities |
|---|---|---|---|---|
| **Healthcare** | `ORG1` | `org1` | `doc_sarah` (Doctor) | OPD Queue, Clinical E-Rx, Vitals Triage, Lab Records |
| **Salon & Wellness** | `ORG2` | `org2` | `olivia_spa` (Therapist) | Treatment Suites, Chemical Color Cards, Ritual Passes |
| **Finance** | `ORG3` | `org3` | `alex_wealth` (Advisor) | Investor KYC, Risk Profiling, Yield Optimizers |
| **Insurance** | `ORG4` | `org4` | `victoria_insur` (Underwriter) | Actuarial Premium Calculator, Underwriting Queue, Policy Vault |
| **Retail** | `ORG5` | `org5` | `rachel_retail` (Stylist) | VIP Fitting Suites, Bespoke Sizing Cards, Lookbooks |
| **Education** | `ORG6` | `org6` | `elena_edu` (Specialist) | Admissions Roadmap, SOP Vault, Milestone Deadlines |
| **Consultancy** | `ORG7` | `org7` | `david_cons` (Consultant) | Conflict Check, Billable Retainer Hours, Legal Contracts |
| **Real Estate** | `ORG8` | `org8` | `marcus_broker` (Broker) | Cap Rate / ROI Calculator, Showings Queue, Title Deeds |
| **Professional Services** | `ORG9` | `org9` | `sophia_law` (Specialist) | SOW Milestones, Architecture Reviews, SLA Tracking |

---

## ⚡ Key Platform Features

- **Multi-Tenant Isolation**: Cryptographic tenant boundaries enforced via validated JWT claims (`organization_id`).
- **Dynamic Terminology Engine**: Reactive UI seamlessly switches between Patients, Guests, Investors, Policyholders, Students, and Clients.
- **Live Queue Board**: Real-time token issuance, status transitions (`Waiting` ➔ `In Consultation` ➔ `Completed`), and queue counters.
- **Digital Records Vault**: Secure, persistent dossier storage tailored per sector (E-Prescriptions, Deeds, SOPs, KYC files).
- **Calculators & Engines**: Built-in actuarial insurance premium calculator, real estate cap-rate / ROI engine, and revenue optimizer.
- **Notification Center**: Multi-category in-app notifications with unread badges, mark-read, and role-scoped filtering.
- **Custom Service Catalog**: Sector-specific catalog presets with custom service creation, price adjustments, and duration rules.

---

## 💳 Enterprise Integrations (Meta & Razorpay)

### 1. Meta WhatsApp Business API (Shared Master Billing)
- **Centralized Billing**: The platform SuperAdmin connects a master credit line to Meta Business Manager to cover all usage centrally.
- **Tenant Isolation**: Each client tenant is onboarded via Meta Embedded Signup with an isolated `waba_id`, `phone_number_id`, and display phone number.
- **Token Security**: Meta System User Access Tokens are encrypted at rest using an authenticated cipher (`app/utils/crypto_helper.py`).
- **Outbound Template Engine**: Native template dispatch handler utilizing each tenant's isolated credentials.

### 2. Razorpay Route (Partner Split Payment Model)
- **Connected Sub-Accounts**: Tenants link their Razorpay accounts (`razorpay_account_id`).
- **Dynamic 5% Platform Fee Split**: When an order is created, the system generates the Razorpay Route `transfers` payload, retaining a 5% commission in the platform master gateway and routing 95% net to the tenant's account.
- **Cryptographic Webhook Controller**: Verifies HMAC-SHA256 signatures (`X-Razorpay-Signature`) and handles `payment.captured`, `transfer.processed`, and `transfer.failed` events.

### 3. SuperAdmin Service Controls (Feature Flags)
- Superadmin can independently set any tenant's service status to `ACTIVE`, `SUSPENDED`, or `INACTIVE` via `PATCH /admin/tenants/:id/toggle-service`.
- **Backend Route Guards**: `@check_whatsapp_active` and `@check_razorpay_active` immediately halt API execution with HTTP `403 Forbidden` if a tenant's service is suspended.

---

## 🐳 Quick Start (Docker Setup)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine + Docker Compose (Linux).

### 1. Clone and Launch
```bash
# Clone the repository
git clone https://github.com/vjamalpure/AppointoCare.git
cd AppointoCare

# Build and start all services in detached mode
docker compose up --build -d
```

### 2. Access the Application
- **Frontend App**: [http://localhost:4200](http://localhost:4200)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

All migrations and multi-industry sample data seed automatically on first launch.

---

## 🔑 Demo Accounts & Credentials

### SuperAdmin
| Role | Username | Password | Access Scope |
|---|---|---|---|
| **SuperAdmin** | `superadmin` | `Admin@12345` | Global oversight, tenant provisioning, subscriptions, broadcast notifications, and service toggles |

### Organization Admins (All Sectors)
*Password for all organization admins is `Org@12345`*
- Healthcare (`ORG1`): `org1`
- Salon & Spa (`ORG2`): `org2`
- Wealth Advisory (`ORG3`): `org3`
- Insurance (`ORG4`): `org4`
- Retail (`ORG5`): `org5`
- Education (`ORG6`): `org6`
- Consultancy (`ORG7`): `org7`
- Real Estate (`ORG8`): `org8`
- Professional Services (`ORG9`): `org9`

### Staff & Industry Specialists
*Password for all specialists is `Staff@12345`*
- Healthcare: `doc_sarah` (Doctor), `staff1` (Staff)
- Salon & Spa: `olivia_spa` (Therapist)
- Wealth Advisory: `alex_wealth` (Advisor)
- Insurance: `victoria_insur` (Underwriter)
- Retail: `rachel_retail` (Stylist)
- Education: `elena_edu` (Specialist)
- Consultancy: `david_cons` (Consultant)
- Real Estate: `marcus_broker` (Broker)
- Professional Services: `sophia_law` (Specialist)

---

## 📡 Core REST API Endpoints

### Authentication
- `POST /auth/login` — Login for SuperAdmin, Organization Admins, and Specialists.

### SuperAdmin Controls
- `GET /admin/organizations` — List all registered tenant organizations.
- `GET /admin/subscriptions` — View organization subscription tiers.
- `PATCH /admin/tenants/<id>/toggle-service` — Toggle WhatsApp or Razorpay service status (`ACTIVE`, `SUSPENDED`, `INACTIVE`).
- `GET /admin/tenants/<id>/services-status` — Inspect real-time status of tenant integrations.
- `POST /api/v1/admin/broadcast-notification` — Send platform-wide announcement to tenants.
- `GET /api/v1/admin/analytics-reports` — Cross-sector aggregated business performance.

### Multi-Industry Suite
- `GET /api/v1/industry-suite/addons` — View active & available sector addons.
- `POST /api/v1/industry-suite/addons/toggle` — Enable / disable modular addon.
- `GET /api/v1/industry-suite/queue` — Live OPD & client queue board tokens.
- `POST /api/v1/industry-suite/queue/create` — Issue next queue token.
- `POST /api/v1/industry-suite/queue/advance` — Advance client token state.
- `GET /api/v1/industry-suite/records` — Sector dossier records vault.
- `POST /api/v1/industry-suite/calculate-insurance-premium` — Actuarial premium calculation.
- `POST /api/v1/industry-suite/calculate-real-estate-roi` — Cap rate & yield evaluator.

### Meta WhatsApp Business API
- `POST /api/v1/whatsapp/embedded-signup-callback` — Onboard client WABA via Meta Embedded Signup.
- `POST /api/v1/whatsapp/send-template` — Send official template message via Meta Cloud API.
- `POST /whatsapp/send` — Send outbound direct WhatsApp message.

### Razorpay Route Payments
- `POST /api/v1/payments/create-split-order` — Create Razorpay Route order with 5% platform split.
- `POST /api/v1/payments/verify` — Verify payment signature and log transaction.
- `POST /api/v1/payments/webhook` — Process `payment.captured` & `transfer.processed` events.

---

## 🧪 Automated Verification & Testing

The project includes end-to-end automated verification suites runnable directly inside Docker:

```bash
# 1. Run 4-Layer Integration Suite (Meta WABA, Razorpay Route, Guards, Token Crypto)
docker exec appointocare-backend-1 python test_integration_layers.py

# 2. Run Comprehensive Multi-Industry Audit (All 9 sectors, 191 checkpoints)
docker exec appointocare-backend-1 python test_audit.py
```

### Reseeding Demo Data
To reset or re-populate the sample data at any time:
```bash
docker exec appointocare-backend-1 python sample_data.py
# Or wipe and re-seed completely:
docker exec appointocare-backend-1 python sample_data.py --reset
```

---

## ⚙️ Environment Configuration

Configuration variables (`appointocare-backend/.env`):

```dotenv
# Application
APP_ENV=development
SECRET_KEY=appointocare-master-secret-key-2026
JWT_SECRET_KEY=appointocare-jwt-secret-key-2026

# Database & Broker
DATABASE_URL=postgresql://postgres:password@db:5432/appointocare
CELERY_BROKER_URL=redis://redis:6379/0

# Demo Seeding
SEED_DEMO_DATA=true

# Meta WhatsApp Configuration (Shared Partner Account)
META_APP_ID=1289401928472910
META_APP_SECRET=your_meta_app_secret
META_GRAPH_VERSION=v20.0

# Razorpay Partner Configuration
RAZORPAY_KEY_ID=rzp_test_AppointoCare99
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_WEBHOOK_SECRET=rzp_webhook_secret_secure_2026
```

---

## 📄 License
Copyright © 2026 **AppointoCare**. All rights reserved.
