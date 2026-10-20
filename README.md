# AppointoCore - Next-Gen Multi-Industry Enterprise Booking & Practice Management SaaS

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![Angular](https://img.shields.io/badge/Angular-18-DD0031?logo=angular&logoColor=white)](https://angular.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)]()

**AppointoCore** is a multi-tenant, market-leading appointment booking, practice management, and ERP platform engineered for 9 high-value industry verticals. Featuring zero-friction tenant onboarding, dynamic terminology adaption, deep enterprise integrations (**Meta WhatsApp Business API** & **Razorpay Route 5%/95% Partner Split**), encrypted tenant credential vaults, and market parity with leading industry platforms.

---

## 🏢 9 Supported Industry Verticals

AppointoCore dynamically adapts its workflows, data models, nomenclature, queue boards, and domain calculators to each tenant's sector:

| # | Sector | Code | Anchor Tenant | Key Parity Benchmark | Specialized Workflows |
|---|---|---|---|---|---|
| 1 | **Healthcare** | `ORG1` | City Care Health & Dental | *Clinicea / Practo* | E-Prescriptions (PDF), SOAP Notes, OPD Queue, Vitals Matrix, Refill Dispensing, ABDM Consent |
| 2 | **Salon & Wellness** | `ORG2` | Apex Aesthetics & Wellness Spa | *Zenoti / Fresha* | Balayage Formulas, Multi-Session Ritual Passes, Suite Allocation, Cancellation Recovery, Retail POS |
| 3 | **Finance & Wealth** | `ORG3` | Vanguard Wealth & Asset Advisory | *Salesforce FSC / Investwell* | Form ADV Disclosures, FINRA 2111 Suitability, Asset Allocation Drift, Household Wealth Mapping |
| 4 | **Insurance Brokerage** | `ORG4` | Sovereign Life & Risk Insurance | *EZLynx / Applied Systems* | Actuarial Premium Engine, Policy Dossiers, FNOL Claims Adjudication, Policy Endorsements |
| 5 | **Retail & Bespoke** | `ORG5` | Aura Haute Couture & Styling Lounge | *Clientbook / Shopify POS* | Anatomical Sizing Matrix, Bespoke Garment Pipeline, Client Wishlists, Private Chambre Privée Lounge |
| 6 | **Education & Counseling** | `ORG6` | Beacon Global University Counseling | *ApplyBoard / Naviance* | Global Degree Catalog, Student Admissions Scorecards, SOP Review Rubrics, Merit Scholarship Match |
| 7 | **Legal & Advisory** | `ORG7` | Sterling & Blackwood Legal Partners | *Clio / MyCase* | Retainer Depletion Ledgers, Adverse Party Conflict Checks, Ethical Wall Clearance, Privileged Dockets |
| 8 | **Real Estate & Architecture** | `ORG8` | Sovereign Realty & Architectural Partners | *Buildertrend / Follow Up Boss* | Escrow Deposit Tracking, Cap-Rate / ROI Evaluator, Architectural Drawings Revisions, VIP Penthouse Tours |
| 9 | **Professional & IT Services** | `ORG9` | Vanguard Global Enterprise Solutions | *Accelo / Mavenlink* | SOC2 Cloud Dossiers, Project Margin Warning Engine, P1–P4 SLA Escalations, Resource Capacity Planning |

---

## ⚡ Key Platform Architecture & Features

- **Multi-Tenant Isolation**: Cryptographic tenant boundaries enforced at database, ORM, and middleware layers via validated JWT claims (`organization_id`).
- **Dynamic Terminology Engine**: Reactive Angular UI dynamically morphs between Patients, Guests, Investors, Policyholders, Students, and Clients.
- **Enterprise Speed & Gzip Compression**: Both Nginx frontend proxy and Flask backend enable dynamic Gzip compression for instantaneous payload transfer.
- **Interactive Quick-Fill Credentials Modal**: Built-in login screen modal allowing instant one-click switching across SuperAdmin, all 9 Org Admins, and Specialist accounts.
- **Live Queue & Token Board**: Real-time token issuance, status transitions (`Waiting` ➔ `In Consultation` ➔ `Completed`), and estimated wait times.
- **Digital Records Vault**: Secure, persistent dossier storage tailored per sector (E-Prescriptions, Deeds, SOPs, KYC files, Lab Orders).
- **Domain Calculators**: Built-in actuarial insurance premium calculator, real estate cap-rate / ROI engine, and revenue optimizer.
- **Modular Add-On Marketplace**: SuperAdmin and Org Admins can toggle industry add-ons on demand with granular per-tenant feature flags.
- **Comprehensive Notification Center**: Multi-channel in-app notifications with unread counters, category filtering, and tenant segregation.

---

## 💳 Enterprise Integrations (Meta & Razorpay)

### 1. Meta WhatsApp Business API (Shared Master Billing)
- **Centralized Line-of-Credit**: The platform SuperAdmin connects a single master Meta credit line to cover all tenant messaging volume centrally.
- **Embedded Tenant Signup**: Each tenant connects an isolated WABA (`waba_id`, `phone_number_id`, and verified phone number) via official Embedded Signup.
- **Token Security at Rest**: Meta System User Access Tokens are encrypted using AES-GCM-256 authenticated ciphers (`app/utils/crypto_helper.py`).
- **Outbound Template Engine**: Native template dispatch handler utilizing isolated tenant credentials.

### 2. Razorpay Route (Partner Split Payment Model)
- **Connected Sub-Accounts**: Tenants link their Razorpay merchant accounts (`razorpay_account_id`).
- **Dynamic 5% Platform Fee Split**: When an order is created, the system generates the Razorpay Route `transfers` payload, retaining a 5% commission in the platform master gateway and routing 95% net to the tenant's account.
- **Idempotent Webhook Controller**: Verifies HMAC-SHA256 signatures (`X-Razorpay-Signature`) and handles `payment.captured`, `transfer.processed`, and `transfer.failed` events with deduplication.

### 3. SuperAdmin Service Controls (Independent Feature Flags)
- Superadmin can independently set any tenant's service status to `ACTIVE`, `SUSPENDED`, or `INACTIVE` via `PATCH /admin/tenants/:id/toggle-service`.
- **Backend Route Guards**: `@check_whatsapp_active` and `@check_razorpay_active` immediately halt API execution with HTTP `403 Forbidden` if a tenant's service is suspended.

---

## 🚀 Quick Start (Docker Setup)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine + Docker Compose (Linux).

### 1. Clone and Launch
```bash
# Clone the repository
git clone https://github.com/vjamalpure/AppointoCore.git
cd AppointoCore

# Build and start all services in detached mode
docker compose up --build -d
```

### 2. Access the Application
- **Frontend App**: [http://localhost:4200](http://localhost:4200)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

All migrations and multi-industry sample data seed automatically on first launch.

### 3. Container & Service Architecture

| Service | Container Name | Port Mapping | Image | Role |
|---|---|---|---|---|
| **frontend** | `appointocore-frontend` | `4200:80` | `appointocore-frontend:latest` | Angular 18 Single-Page App served via Nginx with dynamic Gzip |
| **backend** | `appointocore-backend` | `8000:8000` | `appointocore-backend:latest` | Flask 3.0 REST API with multi-tenant route guards & vaults |
| **celery** | `appointocore-celery` | Internal | `appointocore-celery:latest` | Celery asynchronous worker for task queue & message dispatch |
| **db** | `appointocore-postgres-db` | `5432:5432` | `postgres:16` | PostgreSQL 16 relational database (`appointocore_postgres_data`) |
| **redis** | `appointocore-redis` | `6379:6379` | `redis:7-alpine` | Redis 7 in-memory message broker & Celery result cache |

---

## 🔑 Demo Accounts & Credentials

*(You can also click the **"View Demo Accounts"** button on the web login screen for instant auto-fill!)*

### SuperAdmin
| Role | Username | Password | Access Scope |
|---|---|---|---|
| **SuperAdmin** | `superadmin` | `Admin@12345` | Global oversight, tenant provisioning, subscriptions, broadcast notifications, and service toggles |

### Organization Admins (All 9 Sectors)
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
- Healthcare (`ORG1`): `doc_sarah` (Doctor), `staff1` (Staff Specialist)
- Salon & Spa (`ORG2`): `olivia_spa` (Therapist)
- Wealth Advisory (`ORG3`): `alex_wealth` (Advisor)
- Insurance (`ORG4`): `victoria_insur` (Underwriter)
- Retail (`ORG5`): `jeanluc_style` (Stylist)
- Education (`ORG6`): `elena_counsel` (Counselor)
- Consultancy (`ORG7`): `eleanor_legal` (Partner)
- Real Estate (`ORG8`): `marcus_realty` (Broker)
- Professional Services (`ORG9`): `elizabeth_exec` (Consultant)

---

## 🧪 Automated Verification & Testing

The project includes end-to-end automated verification suites runnable directly inside Docker:

```bash
# 1. Complete Unit & Integration Test Suite (98 test methods across all services)
docker exec appointocore-backend python -m unittest discover -s tests -p "test_*.py"

# 2. Industry Leaders Competitor Matrix Verification Suite (16 Parity Checks)
docker exec appointocore-backend python -m unittest tests/test_industry_leaders_matrix.py

# 3. 4-Layer Integration Suite (Meta WABA, Razorpay Route, Guards, Token Crypto)
docker exec appointocore-backend python test_integration_layers.py

# 4. Comprehensive Multi-Industry Audit (All 9 sectors, 191 checkpoints)
docker exec appointocore-backend python test_audit.py

# 5. Multi-Tenant Authentication & Add-On Migration Suite
docker exec appointocore-backend python tests/test_migration_suite.py
```

### Reseeding Demo Data
To re-populate or reset sample data across all 58 domain models at any time:
```bash
docker exec appointocore-backend python sample_data.py

# Or wipe and re-seed completely with cascading reset:
docker exec appointocore-backend python sample_data.py --reset
```

---

## 🛠️ Environment Configuration

Configuration variables (`appointocore-backend/.env`):

```dotenv
# Application
APP_ENV=development
SECRET_KEY=appointocore-master-secret-key-2026
JWT_SECRET_KEY=appointocore-jwt-secret-key-2026

# Database & Broker
DATABASE_URL=postgresql://postgres:password@db:5432/appointocore
CELERY_BROKER_URL=redis://redis:6379/0

# Demo Seeding
SEED_DEMO_DATA=true

# Meta WhatsApp Configuration (Shared Partner Account)
META_APP_ID=1289401928472910
META_APP_SECRET=your_meta_app_secret
META_GRAPH_VERSION=v20.0

# Razorpay Partner Configuration
RAZORPAY_KEY_ID=rzp_test_AppointoCore99
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_WEBHOOK_SECRET=rzp_webhook_secret_secure_2026
```

---

## 📄 License
Copyright © 2026 **AppointoCore**. All rights reserved.
