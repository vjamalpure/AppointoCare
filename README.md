# AppointoCare — Enterprise Multi-Industry SaaS Platform

<div align="center">

![AppointoCare Platform](https://img.shields.io/badge/Platform-AppointoCare-4f46e5?style=for-the-badge&logo=shield)
![Angular](https://img.shields.io/badge/Angular_18-DD0031?style=for-the-badge&logo=angular&logoColor=white)
![Flask](https://img.shields.io/badge/Python_Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis_7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**The Intelligent Operating System for Modern Appointments, Multi-Industry CRM & Operations.**

*Built for Clinics, Salons, Wealth Advisory, Luxury Retail, Insurance, Universities, Law Chambers, Real Estate, and Enterprise Consulting.*

</div>

---

## 📑 Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [Supported Industry Verticals (9 Sectors)](#2-supported-industry-verticals-9-sectors)
3. [Core Platform Features](#3-core-platform-features)
4. [Market-Benchmarked Modular SaaS Add-ons](#4-market-benchmarked-modular-saas-add-ons)
5. [Architecture & Technology Stack](#5-architecture--technology-stack)
6. [Quick Start with Docker Compose (Recommended)](#6-quick-start-with-docker-compose-recommended)
7. [Local Development Setup (Without Docker)](#7-local-development-setup-without-docker)
8. [Demo Accounts & Credentials Reference](#8-demo-accounts--credentials-reference)
9. [REST API Documentation & Endpoints](#9-rest-api-documentation--endpoints)
10. [Environment Configuration Reference](#10-environment-configuration-reference)
11. [Production Deployment Guidelines](#11-production-deployment-guidelines)

---

## 1. Executive Overview

**AppointoCare** is an enterprise-grade, multi-tenant SaaS scheduling, CRM, and business operations platform. It eliminates rigid single-vertical constraints by natively supporting **9 distinct business sectors** through a reactive metadata engine that dynamically re-skins:

- Terminology (Patients vs. Guests vs. Investors vs. Corporate Clients)
- Intake forms and custom fields (Vitals & MRN vs. Asset Classes vs. Wardrobe Sizes)
- WhatsApp automated bot menus & pre-visit instructions
- Specialized operational workspaces & persistent cloud vaults
- Market-benchmarked toggleable SaaS add-on modules

---

## 2. Supported Industry Verticals (9 Sectors)

| # | Sector | Code | Demo Admin | Demo Staff | Benchmarked Standard | Specialized Workspace & Dossier |
|---|---|---|---|---|---|---|
| 1 | **Healthcare & Clinic** | `ORG1` | `org1` | `doc_sarah`, `dr_chen` | Practo Ray, Epic Systems | Clinical E-Prescriptions, Vitals (BP, SpO2, Pulse), Triage Matrix |
| 2 | **Salon, Spa & Wellness** | `ORG2` | `org2` | `elena_stylist`, `marcus_spa` | Fresha, Zenoti | Treatment Suite Allocator, Chemical Formulation Cards, Spa Add-ons |
| 3 | **Wealth & Advisory** | `ORG3` | `org3` | `alex_wealth`, `diana_advisor` | AdvisorEngine, Addepar | Accredited Investor KYC, Risk Profiling, Asset Allocator |
| 4 | **Luxury Retail & Styling**| `ORG4` | `org4` | `chloe_couture`, `nathan_vip` | Farfetch Private Client | VIP Fitting Suite Allocator, Bespoke Sizing Cards, Lookbooks |
| 5 | **Insurance Agency** | `ORG5` | `org5` | `victor_risk`, `grace_claims` | Applied Epic, Guidewire | Underwriting Risk Dossier, Sum Assured Calculator, Claims Vault |
| 6 | **Academy & Admissions** | `ORG6` | `org6` | `prof_miller`, `dean_ross` | Naviance, Slate Technolutions | University Admissions Roadmap, GPA/SAT Score Tracking, Reach/Match/Safety |
| 7 | **Legal & Consulting** | `ORG7` | `org7` | `attorney_blake`, `counsel_rachel` | Clio, Smokeball | Conflict of Interest Clearance, Billable Retainer Hours Ledger |
| 8 | **Real Estate & Realty** | `ORG8` | `org8` | `broker_diana`, `arch_liam` | Buildium, AppFolio | Property Tour Itinerary Planner, Lockbox Access Codes, Wishlists |
| 9 | **Enterprise Solutions** | `ORG9` | `org9` | `elizabeth_exec` | Accenture Client Exchange | SOW Deliverable Scope, Platinum SLA Tiers, Architecture Audits |

---

## 3. Core Platform Features

### 🏢 Multi-Tenant & Multi-Industry Engine
- **Tenant Isolation**: Secure, role-based boundary separation where all queries enforce cryptographic tenant isolation derived from validated JWT tokens.
- **Dynamic Terminology Engine**: Reactive frontend automatically adopts industry terms (`Customer`, `Patient`, `Investor`, `Guest`, `Client`) across all UI elements, tables, and notifications.

### 🤖 WhatsApp Meta Cloud AI Receptionist Bot
- **24/7 Automated Bookings**: Self-service slot discovery and appointment booking directly from WhatsApp.
- **Smart Receptionist Simulator**: Interactive reception bot with sector-tailored catalogs, branch addresses, and prep instructions.
- **Automated Alerts**: Instant WhatsApp confirmations and appointment reminder dispatches.

### 💳 Payment Processing & Invoicing
- **Razorpay Integration**: Sandbox and production-ready payment orders, signature verification, and automated receipt generation.
- **Invoices & Ledgers**: Transaction logging, paid vs. unpaid status management, and monthly revenue analytics.

### 🛡️ Security, RBAC & Audit Trail
- **Role-Based Access Control**: Strict multi-tier RBAC (`SuperAdmin`, `OrgAdmin`, `Manager`, `Staff`).
- **Comprehensive Audit Trail**: Every status modification, add-on toggle, sector import, and payment verification is cryptographically logged with IP and user metadata.

### 📊 Modern Visual Identity & Glassmorphism
- **Futuristic Brand Logo**: Custom SVG mark combining a calendar grid, operational pulse line, and verification checkmark.
- **Glassmorphic Design System**: Frosted glass top navigation bar, collapsible sleek sidebar, modern KPI stat cards with trend indicators, and standardized modal popups with entrance animations.
- **Modern Dual-Panel Login**: Left product showcase panel with ambient mesh glow and feature cards; right elevated authentication hub with 1-click multi-industry demo selectors.

---

## 4. Market-Benchmarked Modular SaaS Add-ons

AppointoCare includes **36 modular SaaS add-on engines** (4 per sector) that can be toggled on or off per organization with an audit trail:

```
├── Healthcare
│   ├── Digital E-Prescription & Rx Writer (Practo Ray)
│   ├── Vitals & Emergency Triage Matrix (Epic Systems)
│   ├── Diagnostic Lab Packages & Report Vault (Practo Diagnostics)
│   └── TPA / Insurance Pre-Authorization Checklist (Athenahealth)
├── Salon & Spa
│   ├── Treatment Suite & Hydrotherapy Allocator (Zenoti)
│   ├── Chemical Formulation & Color Card (Fresha)
│   ├── Spa Add-on & Upsell Service Engine (Booker)
│   └── Stylist Station Conflict Manager (Mindbody)
├── Wealth & Finance
│   ├── Accredited Investor KYC Dossier (AdvisorEngine)
│   ├── Target Asset Allocation Profiler (Addepar)
│   ├── Fiduciary Compliance & Disclosures (eMoney)
│   └── Risk Tolerance Scoring Engine (Riskalyze)
├── Luxury Retail
│   ├── VIP Fitting Suite Booking & Hospitality (Farfetch VIP)
│   ├── Bespoke Wardrobe Sizing Card (Net-a-Porter)
│   ├── Curated Lookbook Session Manager (Saks Fifth Ave)
│   └── Private Client Gifting Registry (Harrods)
├── Insurance
│   ├── Underwriting Risk & Policy Dossier (Applied Epic)
│   ├── Pre-Claims Evidence & Incident Vault (Guidewire)
│   ├── Multi-Risk Actuarial Premium Calculator (Vertafore)
│   └── Policyholder Medical & Hazard Declaration (Lemonade)
├── Education & Counseling
│   ├── University Admissions Roadmap & Milestones (Naviance)
│   ├── Standardized Test Score Tracker (Slate Technolutions)
│   ├── Statement of Purpose & Recommendation Vault (Cialfo)
│   └── Visa & Financial Clearance Checklist (IDP Connect)
├── Legal & Management Consulting
│   ├── Conflict of Interest Clearance Engine (Clio)
│   ├── Billable Retainer Hours Ledger (Smokeball)
│   ├── Client Trust Account (IOLTA) Tracker (PracticePanther)
│   └── Privileged Legal Dossier & Evidence Vault (MyCase)
├── Real Estate & Realty
│   ├── Property Tour Itinerary & Routing Planner (ShowingTime)
│   ├── Lockbox & Private Access Code Vault (Buildium)
│   ├── Buyer Preference & Property Matcher (AppFolio)
│   └── Escrow & Closing Milestones Checklist (Dotloop)
└── Enterprise Solutions
    ├── SOW Milestone & Deliverable Delivery Tracker (Accenture)
    ├── SLA Performance & Response Monitor (ServiceNow)
    ├── Enterprise Architecture Compliance Review (SAP)
    └── Multi-Stakeholder Sign-Off & Approval Matrix (Salesforce)
```

---

## 5. Architecture & Technology Stack

```
                                  [ Browser / Client ]
                                           │
                                  Port 4200 (HTTP)
                                           │
                         ┌─────────────────┴─────────────────┐
                         │      Nginx Reverse Proxy          │
                         │   (appointocare-frontend-1)       │
                         │     Angular 18 SPA Assets         │
                         └─────────────────┬─────────────────┘
                                           │
                                  Port 8000 (API / Reverse Proxy)
                                           │
                         ┌─────────────────┴─────────────────┐
                         │         Flask REST API            │
                         │    (appointocare-backend-1)       │
                         │   Python 3.12, SQLAlchemy, JWT    │
                         └───────┬───────────────────┬───────┘
                                 │                   │
                     Port 5432   │                   │  Port 6379
                                 ▼                   ▼
                     ┌──────────────────┐    ┌──────────────────┐
                     │  PostgreSQL 16   │    │     Redis 7      │
                     │ (appointocare-db)│    │ (appointocare-   │
                     │  Relational Data │    │      redis)      │
                     └──────────────────┘    └─────────┬────────┘
                                                       │
                                                       ▼
                                             ┌──────────────────┐
                                             │  Celery Worker   │
                                             │ (appointocare-   │
                                             │     celery)      │
                                             └──────────────────┘
```

### Component Details
- **Frontend**: Angular 18, Angular Material 18, RxJS, Chart.js / ng2-charts, Custom Glassmorphic SCSS.
- **Backend API**: Python 3.12, Flask, Flask-JWT-Extended, Flask-SQLAlchemy, Marshmallow, Alembic.
- **Database**: PostgreSQL 16 with JSONB support for dynamic sector custom fields and specialized dossiers.
- **Cache / Message Broker**: Redis 7.
- **Asynchronous Tasks**: Celery Worker for background jobs and notification broadcasts.
- **Orchestration**: Docker Compose with health checks and volume persistence.

---

## 6. Quick Start with Docker Compose (Recommended)

### Prerequisites
- **Docker Desktop** (Windows / macOS) or **Docker Engine + Docker Compose** (Linux).
- At least 4GB RAM and 5GB free disk space.

### 1. Clone the Repository
```bash
git clone https://github.com/vjamalpure/AppointoCare.git
cd AppointoCare
```

### 2. Launch All Services
```bash
# Build and run all 5 containers in the background
docker compose up --build -d
```

### 3. Verify Container Health
```bash
docker compose ps
```
You should see all 5 containers active and healthy:
- `appointocare-frontend-1` (Port 4200)
- `appointocare-backend-1` (Port 8000)
- `appointocare-db-1` (Port 5432)
- `appointocare-redis-1` (Port 6379)
- `appointocare-celery-1`

### 4. Open in Browser
- **Frontend App**: [http://localhost:4200](http://localhost:4200)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

---

## 7. Local Development Setup (Without Docker)

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL 14+ running on port 5432
- Redis 6+ running on port 6379

### Backend Setup
```bash
cd appointocare-backend

# 1. Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Initialize database and migrations
python init_db_local.py

# 5. Start Flask development server
python run.py
# Server runs at http://localhost:8000
```

### Celery Background Worker (Second Terminal)
```bash
cd appointocare-backend
.\venv\Scripts\Activate.ps1
celery -A celery_worker.celery worker --loglevel=info
```

### Frontend Setup (Third Terminal)
```bash
cd appointocare-frontend

# 1. Install dependencies
npm ci

# 2. Start Angular development server
npm start
# App opens at http://localhost:4200
```

---

## 8. Demo Accounts & Credentials Reference

The application seeds default accounts for instant evaluation:

### Super Admin
| Role | Username | Password | Organization Code | Capabilities |
|---|---|---|---|---|
| **Super Admin** | `superadmin` | `Admin@12345` | *(Leave blank)* | Platform overview, global appointments, tenant provisioning, plan management, system audit logs |

### Organization Admins (All 9 Sectors)
| Sector | Code | Organization Name | Username | Password |
|---|---|---|---|---|
| **Healthcare** | `ORG1` | City Care Health & Dental | `org1` | `Org@12345` |
| **Salon & Spa** | `ORG2` | Apex Aesthetics & Wellness Spa | `org2` | `Org@12345` |
| **Finance** | `ORG3` | Vanguard Wealth Advisory | `org3` | `Org@12345` |
| **Luxury Retail** | `ORG4` | Aura Haute Couture & Styling | `org4` | `Org@12345` |
| **Insurance** | `ORG5` | Sovereign Life Insurance | `org5` | `Org@12345` |
| **Education** | `ORG6` | Beacon Global University Counseling | `org6` | `Org@12345` |
| **Legal** | `ORG7` | Sterling & Blackwood Legal | `org7` | `Org@12345` |
| **Real Estate** | `ORG8` | Sovereign Realty & Architecture | `org8` | `Org@12345` |
| **Enterprise** | `ORG9` | Vanguard Global Enterprise | `org9` | `Org@12345` |

### Specialized Staff Members
| Role | Specialization | Username | Password | Org Code |
|---|---|---|---|---|
| **Doctor** | Chief Surgeon / General Medicine | `doc_sarah` | `Staff@12345` | `ORG1` |
| **Physician** | Senior Dental Specialist | `dr_chen` | `Staff@12345` | `ORG1` |
| **Stylist** | Master Aesthetician | `elena_stylist`| `Staff@12345` | `ORG2` |
| **Advisor** | Senior Wealth Portfolio Manager | `alex_wealth` | `Staff@12345` | `ORG3` |
| **Realtor** | Commercial Broker | `marcus_realty`| `Staff@12345` | `ORG8` |
| **Consultant**| Principal Enterprise Consultant | `elizabeth_exec`| `Staff@12345` | `ORG9` |

> 💡 **Tip:** On the [Login Page](http://localhost:4200/login), you can click any of the **1-Click Multi-Industry Demo Access** chips to populate credentials and switch view instantly!

---

## 9. REST API Documentation & Endpoints

### Authentication
```http
POST /auth/login
Content-Type: application/json

{
  "username": "org1",
  "password": "Org@12345",
  "org_code": "ORG1"
}
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "role": "Organization",
  "organization_code": "ORG1",
  "organization_name": "City Care Health & Dental",
  "sector": "Healthcare"
}
```

### Modular Industry Suite & SaaS Add-ons
- `GET /api/v1/industry-suite/addons`: Retrieve all 4 market-benchmarked add-ons for the tenant's active sector.
- `POST /api/v1/industry-suite/addons/toggle`: Toggle an add-on module on/off with audit logging:
  ```json
  { "addon_id": "addon_eprescription", "enabled": true }
  ```
- `GET /api/v1/industry-suite/records`: Query specialized dossiers and records (filter by `record_type`, `sector`).
- `POST /api/v1/industry-suite/records`: Create a specialized industry record (E-Prescription, Retainer, Lookbook, SOW):
  ```json
  {
    "record_type": "prescription",
    "title": "Clinical Rx: Patient Consultation",
    "data": { "vitals_bp": "120/80", "diagnosis": "Acute Bronchitis", "medications": [...] }
  }
  ```
- `DELETE /api/v1/industry-suite/records/<id>`: Delete a specialized dossier.
- `GET /api/v1/industry-suite/benchmarks`: Retrieve peer platform comparisons and operational efficiency gain benchmarks.

### Multi-Sector Services Catalog
- `GET /api/v1/services`: List services for the organization.
- `POST /api/v1/services`: Create a new custom service.
- `PUT /api/v1/services/<id>`: Update an existing service.
- `DELETE /api/v1/services/<id>`: Remove a service.
- `POST /api/v1/services/import-sector`: 1-click import standard catalog presets for any of the 9 sectors.

### Customer CRM & 360 Timeline
- `GET /api/v1/customers`: List customers with contact details and metadata.
- `POST /api/v1/customers`: Create a customer record.
- `GET /api/v1/customers/<id>/timeline`: Full 360 customer timeline (appointments, WhatsApp conversations, payments).

### WhatsApp Receptionist Bot
- `POST /api/v1/whatsapp/simulate-chat`: Context-aware conversational AI receptionist:
  ```json
  { "message": "1", "phone": "+919876543210" }
  ```
- `GET /api/v1/whatsapp/logs`: View incoming and outgoing message logs.
- `GET /api/v1/whatsapp/config`: View Meta WhatsApp Cloud API credentials.

### Payments & Razorpay Sandbox
- `GET /api/v1/payments/config`: View gateway configuration and sandbox readiness.
- `POST /api/v1/payments/create-order`: Create a Razorpay order.
- `POST /api/v1/payments/verify`: Verify Razorpay signature and generate invoice.

### Security Audit Logs
- `GET /api/v1/audit-logs`: Searchable platform audit trail with action, category, IP address, and metadata.

---

## 10. Environment Configuration Reference

Edit `appointocare-backend/.env` or `.env`:

```dotenv
# Application Environment
APP_ENV=development
SECRET_KEY=appointocare-ultra-secure-key-2026
JWT_SECRET_KEY=appointocare-jwt-signature-key-2026

# Database & Cache Connection
DATABASE_URL=postgresql://postgres:password@db:5432/appointocare
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Seeding & Initial Credentials
SEED_DEMO_DATA=true
ADMIN_USERNAME=superadmin
ADMIN_PASSWORD=Admin@12345
ORG_USERNAME=org1
ORG_PASSWORD=Org@12345
STAFF_USERNAME=staff1
STAFF_PASSWORD=Staff@12345

# Razorpay Integration (Optional)
RAZORPAY_ENABLED=true
RAZORPAY_KEY_ID=rzp_test_sandbox_key
RAZORPAY_KEY_SECRET=rzp_test_sandbox_secret

# WhatsApp Meta Cloud API (Optional)
WHATSAPP_ENABLED=true
WHATSAPP_PROVIDER=mock # Use 'meta' for live production Meta Cloud API
WHATSAPP_PHONE_NUMBER_ID=1092837465
WHATSAPP_ACCESS_TOKEN=EAAB...
```

---

## 11. Production Deployment Guidelines

For production deployments:
1. **Secrets Management**: Supply environment variables through Docker Secrets, AWS Secrets Manager, or HashiCorp Vault instead of checked-in `.env` files.
2. **Database Resilience**: Use a managed PostgreSQL service (Amazon RDS, Google Cloud SQL, or Azure Database for PostgreSQL) with automated point-in-time recovery.
3. **TLS/SSL Encryption**: Configure SSL certificates via Let's Encrypt or your cloud load balancer.
4. **Data Seeding**: Set `SEED_DEMO_DATA=false` in production environments.
5. **Worker Scaling**: Scale Celery worker replicas based on WhatsApp and notification queue depths:
   ```bash
   docker compose up --scale celery=3 -d
   ```

---

## 📄 License & Attribution

Copyright © 2026 **AppointoCare**. All rights reserved.
Developed for high-velocity multi-industry SaaS deployment.
