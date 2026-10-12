# AppointoCare — Current State Architecture

**Audit Date:** October 12, 2026  
**Topology:** Containerized Modular-Monolith SaaS (Docker Compose)  
**Status:** Operational (Pilot Deployment)  

---

## 1. Executive Summary

AppointoCare is an operational multi-tenant modular-monolith SaaS platform engineered to support 9 industry verticals in India:
1. **Healthcare** (`ORG1` - City Care Health & Dental)
2. **Salon & Wellness** (`ORG2` - Apex Aesthetics & Wellness Spa)
3. **Finance** (`ORG3` - Vanguard Wealth & Asset Advisory)
4. **Insurance** (`ORG4` - Sovereign Life & Risk Insurance)
5. **Retail** (`ORG5` - Aura Haute Couture & Styling Lounge)
6. **Education** (`ORG6` - Beacon Global University Counseling)
7. **Consultancy** (`ORG7` - Sterling & Blackwood Legal Partners)
8. **Real Estate** (`ORG8` - Sovereign Realty & Architectural Partners)
9. **Professional Services** (`ORG9` - Vanguard Global Enterprise Solutions)

The application utilizes a shared multi-tenant core with dynamic vertical modules and records storage.

---

## 2. Verified Technology Stack

| Layer | Component | Verified Version & Implementation |
| :--- | :--- | :--- |
| **Frontend Framework** | Angular | **18.2.14** (TypeScript 5.5.2, Angular CLI 18.2.21, RxJS 7.8.0, Zone.js 0.14.10) |
| **Frontend UI System** | Angular Material & CDK | **18.2.14** with custom SCSS design tokens, responsive typography, and Material Icons |
| **Data Visualization** | Chart.js & ng2-charts | **Chart.js 4.5.1**, **ng2-charts 6.0.1** |
| **Frontend Routing & Auth** | Angular Router | Modular lazy loading (`OrgDashboardModule`, `AdminModule`), `JwtInterceptor`, `AuthGuard` |
| **Backend Framework** | Python / Flask | **Python 3.11+**, **Flask 2.3.3**, Werkzeug 2.3.7, Gunicorn 23.0.0 |
| **ORM & Migrations** | Flask-SQLAlchemy | **Flask-SQLAlchemy 3.0.5**, **Flask-Migrate 4.0.4** (Alembic) |
| **Authentication & Tokens**| Flask-JWT-Extended | **4.4.4** with short-lived access tokens and refresh rotation |
| **Database Engine** | PostgreSQL | **PostgreSQL 16** (`psycopg2-binary 2.9.9`) |
| **Cache & Task Broker** | Redis | **Redis 7-alpine** (Port 6379) |
| **Background Jobs** | Celery | **Celery 5.4.0** worker process |
| **External Integrations** | Meta & Razorpay | Meta WhatsApp Cloud API (v21.0), Razorpay Orders & Route split payments |

---

## 3. Deployment & Runtime Topology

The operational application runs under Docker Compose (`docker-compose.yml`):
- `appointocare-frontend-1` on port `4200:80` (Nginx serving production Angular build)
- `appointocare-backend-1` on port `8000:8000` (Flask application with live host volume mount `./appointocare-backend:/app`)
- `appointocare-celery-1` (Celery background worker executing task queues from Redis)
- `appointocare-db-1` on port `5432:5432` (PostgreSQL 16 container with `postgres_data` persistent volume)
- `appointocare-redis-1` on port `6379:6379` (Redis 7 container for broker and caching)

*Note on root `server.js`:* An Express 4.21.2 Node.js script resides at project root. It is a legacy in-memory mock server used during early standalone prototyping. The real operational application runs entirely on the Flask + Angular + Docker stack.

---

## 4. Multi-Tenancy Architecture

- **Strategy:** Shared-Database, Discriminator-Column (`organization_id` / `tenant_id`).
- **Core Entities:** `Organization`, `User`, `Branch`, `Customer`, `Service`, `Appointment`, `AppointmentTransaction`, `IndustryRecord`, `WhatsAppConfig`, `PaymentConfig`, `AuditLog`.
- **Vertical Extensibility:** Reusable `IndustryRecord` entity with typed JSON payloads (`data`), coupled with `SectorTemplate` and dynamic sector addons, preventing destructive schema alterations when extending industry workflows.

---

## 5. Test Baseline

Verified through direct test execution:
- `docker exec appointocare-backend-1 python test_audit.py`: **191 / 191 Passed (100%)**
- `python scratch/full_industry_verification.py`: **216 / 216 Passed (100%)**
All 9 industry verticals and platform SuperAdmin workflows are currently verified green.
