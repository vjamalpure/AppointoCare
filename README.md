# AppointoCare

AppointoCare is an appointment and organization management application with an Angular frontend, Flask REST API, PostgreSQL database, Redis, and a Celery worker.

## Quick Start

Choose your preferred method:

- **Docker Compose (Recommended for Development)**: Everything runs in containers. Simplest setup.
- **Local Development**: Full control; requires installing PostgreSQL, Redis, Python, and Node.js locally.

## Project Layout

- `appointocare-frontend/`: Angular 18 application served by Nginx in production.
- `appointocare-backend/`: Flask API, SQLAlchemy models, Alembic migrations, and Celery tasks.
- `docker-compose.yml`: Local container orchestration for PostgreSQL, Redis, Flask, Celery, and Nginx.

---

# Run with Docker Compose (Recommended)

## Prerequisites for Docker Setup

- **Docker Desktop** (Windows, macOS) or **Docker Engine + Docker Compose** (Linux)
- Download and install from: https://www.docker.com/products/docker-desktop
- Verify installation: `docker --version` and `docker compose --version`
- At least 4GB free RAM and 2GB disk space

## Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
git clone https://github.com/vjamalpure/AppointoCare.git
cd AppointoCare

# Optional: Copy the environment example to .env for customization
# On Windows PowerShell
Copy-Item .env.example .env

# On macOS/Linux
cp .env.example .env
```

## Step 2: Start Docker Containers

```bash
# Build and start all containers in the background
docker compose up --build -d

# Or run in foreground to see logs (press Ctrl+C to stop)
docker compose up --build
```

**✨ Fully Automatic Database Initialization:**

Docker automatically handles **everything** on first run:

1. **PostgreSQL Startup** - Database server starts and becomes healthy (15-30 seconds)
2. **Create Database** - Runs `init_db.py` to create `appointocare` schema if it doesn't exist
3. **Database Migrations** - Runs `flask db upgrade` to create all tables and schema
4. **Demo Data Seeding** - Populates sample data (admin user, organization, services, plans, etc.)
5. **Redis Startup** - Cache and broker service starts
6. **Backend API** - Flask API becomes healthy and ready for requests
7. **Celery Worker** - Background job processor starts
8. **Frontend** - Angular app builds and serves on Nginx

**Total startup time:** 1-2 minutes on first run, 20-30 seconds on subsequent runs.

✅ **You can login immediately after startup completes!**

All database operations are **idempotent** — the database schema is created only once, and subsequent container restarts won't recreate it or reseed data.

## Step 3: Access the Application

Once all containers are running and healthy:

- **Frontend**: http://localhost:4200
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432 (if needed for direct connections)
- **Redis**: localhost:6379 (if needed for direct connections)

## Step 4: Log In

Use one of the demo accounts below. The credentials are automatically seeded during container startup.

| Role | Organization Code | Username | Password |
|---|---|---|---|
| **Super Admin** | *(leave blank)* | `superadmin` | `Admin@12345` |
| **Organization Admin** | `ORG1` | `org1` | `Org@12345` |
| **Organization Staff** | `ORG1` | `staff1` | `Staff@12345` |

## Docker Compose Commands

```bash
# Check status of all containers
docker compose ps

# View live logs from all services
docker compose logs -f

# View logs from a specific service (backend, frontend, db, redis, celery)
docker compose logs -f backend

# Stop all containers (data persists)
docker compose stop

# Start containers again after stopping
docker compose start

# Stop and remove all containers (data persists in volume)
docker compose down

# Stop containers and delete all data
docker compose down -v

# Rebuild images and start fresh
docker compose up --build -d

# Execute a command in a running container
docker compose exec backend flask --app run.py db upgrade
docker compose exec backend python create_users.py
```

## Customizing Docker Environment

Edit `.env` or `.env.example` to override defaults:

```dotenv
# Change admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourPassword123

# Change organization user credentials
ORG_USERNAME=hospital1
ORG_PASSWORD=OrgPassword123

# Disable demo data seed (empty database)
SEED_DEMO_DATA=false

# Production mode (no mock providers)
APP_ENV=production

# PostgreSQL password
POSTGRES_PASSWORD=YourDbPassword
```

Restart containers for changes to take effect:

```bash
docker compose restart backend
```

## Troubleshooting Docker Setup

**Q: Port 4200 or 8000 is already in use**

A: Change the port in `docker-compose.yml` or stop the conflicting service:

```bash
# Find and stop services using the port
lsof -i :4200  # macOS/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 4200).OwningProcess  # Windows

# Change ports in docker-compose.yml and rebuild
docker compose up --build -d
```

**Q: Database migration failed or tables are missing**

A: Recreate the database:

```bash
docker compose down -v
docker compose up --build -d
```

**Q: Demo data not seeding or accounts not found**

A: Ensure `SEED_DEMO_DATA=true` in `.env` and check logs:

```bash
docker compose logs backend | grep -i "demo\|seed\|admin"

# If needed, manually run the seed
docker compose exec backend python create_users.py
```

**Q: Out of disk space or low performance**

A: Clean up Docker resources:

```bash
docker system prune -a
docker volume prune
```

---

# Run Locally (Without Docker)

## Prerequisites for Local Development

### Required Software

1. **Python 3.12+**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **PostgreSQL 12+**
   - Download: https://www.postgresql.org/download/
   - Windows installer recommended
   - Verify: `psql --version`
   - Create a database: `createdb appointocare`

3. **Redis 6+**
   - Download: https://redis.io/download/
   - On Windows, use Windows Subsystem for Linux (WSL) or use pre-built binaries
   - Verify: `redis-cli ping` (should respond with `PONG`)

4. **Node.js 20+ and npm**
   - Download: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

### Verify All Prerequisites

```powershell
# Windows PowerShell
python --version
psql --version
redis-cli --version
node --version
npm --version
```

## Step 1: Clone Repository

```bash
git clone https://github.com/vjamalpure/AppointoCare.git
cd AppointoCare
```

## Step 2: Start PostgreSQL and Redis

### Windows

```powershell
# PostgreSQL should auto-start, verify it's running
psql -U postgres -c "SELECT version();"

# Start Redis (in a separate terminal)
redis-server
```

### macOS/Linux

```bash
# Start PostgreSQL
brew services start postgresql  # macOS with Homebrew
sudo systemctl start postgresql  # Linux

# Start Redis
brew services start redis  # macOS with Homebrew
sudo systemctl start redis  # Linux
```

## Step 3: Setup Backend

```powershell
# Windows PowerShell
cd appointocare-backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file with local configuration
Copy-Item .env.example .env
```

Edit `appointocare-backend/.env` with local values:

```dotenv
APP_ENV=development
SECRET_KEY=local-dev-secret-change-me
JWT_SECRET_KEY=local-jwt-secret-change-me

# PostgreSQL local connection
DATABASE_URL=postgresql://postgres:password@localhost:5432/appointocare

# Redis local connection
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Demo data seeding
SEED_DEMO_DATA=true
ADMIN_USERNAME=superadmin
ADMIN_PASSWORD=Admin@12345
ORG_USERNAME=org1
ORG_PASSWORD=Org@12345
STAFF_USERNAME=staff1
STAFF_PASSWORD=Staff@12345
```

## Step 4: Initialize Database and Seed Demo Data

The easiest way is to use the automated initialization script:

```powershell
# Windows PowerShell (in appointocare-backend directory with venv activated)

# Automated: Checks database, creates if needed, runs migrations, and seeds data
python init_db_local.py
```

**What this does:**
- ✓ Checks if database `appointocare` exists on PostgreSQL
- ✓ Creates it if it doesn't exist
- ✓ Applies all migrations (creates tables and schema)
- ✓ Seeds demo users and data (if `SEED_DEMO_DATA=true`)

**Alternative manual steps** (if you prefer):

```powershell
# Create database manually (if init_db_local.py didn't work)
# Connect to PostgreSQL and run:
psql -U postgres -c "CREATE DATABASE appointocare;"

# Then apply migrations manually
flask --app run.py db upgrade

# Then seed demo data
python create_users.py
```

## Step 5: Start Backend API

```powershell
# In appointocare-backend directory with venv activated
python run.py

# Backend will start at http://localhost:8000
# Press Ctrl+C to stop
```

## Step 6: Start Celery Worker (In a New Terminal)

```powershell
# In appointocare-backend directory with venv activated
celery -A celery_worker.celery worker --loglevel=info

# Worker will start and listen for background tasks
# Press Ctrl+C to stop
```

## Step 7: Setup Frontend

In a new terminal (third terminal window):

```bash
# Navigate to frontend directory
cd appointocare-frontend

# Install dependencies
npm ci

# Start development server
npm start

# Frontend will open at http://localhost:4200
```

## Local Development URLs

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Local Development Demo Logins

| Role | Organization Code | Username | Password |
|---|---|---|---|
| **Super Admin** | *(leave blank)* | `superadmin` | `Admin@12345` |
| **Organization Admin** | `ORG1` | `org1` | `Org@12345` |
| **Organization Staff** | `ORG1` | `staff1` | `Staff@12345` |

## Useful Local Development Commands

```powershell
# Backend: Run tests
cd appointocare-backend
python -m unittest discover -s tests -v

# Backend: Apply a specific migration
flask --app run.py db upgrade

# Backend: Create a new migration after model changes
flask --app run.py db revision --autogenerate -m "Description of changes"

# Frontend: Build for production
cd appointocare-frontend
npm run build

# Frontend: Run unit tests
npm test
```

## Troubleshooting Local Setup

**Q: "Cannot connect to PostgreSQL"**

A: Verify PostgreSQL is running and the connection string is correct:

```powershell
psql -U postgres -d appointocare -h localhost
```

**Q: "Redis connection refused"**

A: Verify Redis is running:

```bash
redis-cli ping
```

**Q: "Port 8000 or 4200 is already in use"**

A: Change the port or kill the process:

```powershell
# Find process using port
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess

# Kill process
Stop-Process -Id <PID> -Force

# Or change port in backend: python run.py --port 8001
```

**Q: "Module not found" errors in backend**

A: Ensure virtual environment is activated and dependencies are installed:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

# API Documentation

## Base URL

- **Local/Docker**: `http://localhost:8000`
- **Production**: `https://yourdomain.com`

## Authentication

All API endpoints (except `/health`, `/ready`, and `/auth/login`) require JWT authentication.

Login endpoint:

```
POST /auth/login
Content-Type: application/json

{
  "org_code": "ORG1",
  "username": "org1",
  "password": "Org@12345"
}
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Include the token in subsequent requests:

```
Authorization: Bearer <access_token>
```

## API Endpoints Summary

### Health Check

- `GET /health` - Service health check
- `GET /ready` - Service readiness check

### Platform Endpoints

## API Endpoints Summary

### Health Check

- `GET /health` - Service health check
- `GET /ready` - Service readiness check

### Platform Endpoints

The platform endpoints are available under `/api/v1/platform`:

- `GET/POST /plans`: Super Admin subscription plan management.
- `GET/POST /templates`: sector service templates; creation is restricted to Super Admin.
- `GET/POST /campaigns`: organization-scoped campaign drafts and scheduling metadata.
- `GET /notifications` and `POST /notifications/{id}/read`: organization notifications.
- `GET/POST /branches`: organization-scoped branches.
- `GET /reports/summary`: tenant-scoped KPI summary, or an optional organization filter for Admin.

All tenant endpoints derive `organization_id` from the JWT claims. They do not trust a client-supplied organization ID.

### Provider Endpoints

Provider adapters live under `appointocare-backend/app/providers` and application services use those adapters instead of vendor SDKs. Development defaults to mock providers; production does not fall back to mocks. Configure a real provider only through environment variables:

- `GET /api/v1/providers/status`: authenticated provider state inspection.
- `POST /api/v1/providers/payments/orders`: create a payment order.
- `POST /api/v1/providers/payments/verify`: verify a payment signature.
- `POST /api/v1/providers/webhooks/razorpay`: signed, idempotent Razorpay webhook endpoint.
- `GET/POST /api/v1/providers/webhooks/whatsapp`: Meta webhook verification and signed event intake.

Without credentials, real-provider operations return a controlled provider configuration error. Mock operations are intended for development and automated tests only. Webhook endpoints never log access tokens or raw provider secrets.

---

# Database Schema

## Database Name: `appointocare`

The project uses a **PostgreSQL database named `appointocare`** (the lowercase project name).

### Database Creation

The database is created automatically in both Docker and local setups:

**Docker:**
- PostgreSQL creates `appointocare` database on container startup
- `init_db.py` runs in the backend entrypoint as a safety check

**Local Development:**
- `init_db_local.py` checks if `appointocare` exists and creates it if needed
- No manual `createdb` commands required

### Database Location

- **Docker:** Inside PostgreSQL container at `db:5432/appointocare`
- **Local:** On host PostgreSQL at `localhost:5432/appointocare`
- **Connection String:** `postgresql://postgres:password@host:5432/appointocare`

### Database Schema Objects

After initialization, the `appointocare` database contains:

- **Tables:** Users, Organizations, Appointments, Services, Subscriptions, Payments, Notifications, Branches, Sector Templates, etc.
- **Migrations:** Managed by Alembic (see `appointocare-backend/migrations/versions/`)
- **Seed Data:** Demo admin, organization, staff, customers, and service data

All tables are created and seeded automatically during startup.

---

For production deployment, ensure:

1. Use environment variables from a secrets manager, not `.env` files
2. Set `APP_ENV=production`
3. Set `SEED_DEMO_DATA=false`
4. Use strong, unique passwords for all services
5. Enable HTTPS/TLS
6. Set up proper database backups
7. Use a production-grade web server (Nginx, HAProxy)
8. Configure firewall rules
9. Set up monitoring and logging
10. Review the Docker image for security best practices

---

# Development Tools

## Frontend Development

```bash
cd appointocare-frontend

# Start development server with hot reload
npm start

# Build for production
npm run build

# Run unit tests
npm test

# Run linting
npm run lint
```

## Backend Development

```bash
cd appointocare-backend

# Run tests
python -m unittest discover -s tests -v

# Database migrations
flask --app run.py db revision --autogenerate -m "Description"
flask --app run.py db upgrade
flask --app run.py db downgrade

# Seed demo data
python create_users.py

# Format code
black app/ tests/

# Lint code
flake8 app/ tests/
```

---

# Configuration Reference

## Environment Variables

### Application

- `APP_ENV`: `development` or `production`
- `SECRET_KEY`: Flask secret key (change in production)
- `JWT_SECRET_KEY`: JWT signing key (change in production)
- `JWT_ACCESS_TOKEN_HOURS`: Access token expiration (default: 1)
- `JWT_REFRESH_TOKEN_DAYS`: Refresh token expiration (default: 30)

### Database

- `DATABASE_URL`: PostgreSQL connection string
- `SQLALCHEMY_ECHO`: Log SQL queries (true/false)

### Cache & Background Jobs

- `CELERY_BROKER_URL`: Redis broker URL
- `CELERY_RESULT_BACKEND`: Redis result backend URL

### Seeding

- `SEED_DEMO_DATA`: Enable demo data seed (true/false)
- `ADMIN_USERNAME`: Demo admin username
- `ADMIN_PASSWORD`: Demo admin password
- `ORG_USERNAME`: Demo organization username
- `ORG_PASSWORD`: Demo organization password
- `STAFF_USERNAME`: Demo staff username
- `STAFF_PASSWORD`: Demo staff password

### Providers (Optional)

- `RAZORPAY_ENABLED`: Enable Razorpay payment provider
- `RAZORPAY_KEY_ID`: Razorpay API key
- `RAZORPAY_KEY_SECRET`: Razorpay API secret
- `RAZORPAY_WEBHOOK_SECRET`: Razorpay webhook secret
- `WHATSAPP_ENABLED`: Enable WhatsApp integration
- `WHATSAPP_PROVIDER`: `mock` or `meta`
- `WHATSAPP_ACCESS_TOKEN`: Meta WhatsApp API token
- `WHATSAPP_PHONE_NUMBER_ID`: Meta WhatsApp phone number ID
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN`: Webhook verification token
- `WHATSAPP_APP_SECRET`: Meta app secret

### CORS

- `CORS_ORIGINS`: Allowed origins (comma-separated)

## Notes

- Do not use the example secrets in production.
- The frontend production image includes an Nginx fallback to `index.html`, so Angular client-side routes work on direct navigation.
- If a PostgreSQL password contains URL-reserved characters, URL-encode it before putting it in `DATABASE_URL`.
- Compose uses `db` and `redis` as service hostnames. Local development uses `localhost`.

---

# Additional Resources

## Database Migrations

Alembic handles all database schema changes. To create a new migration after modifying models:

```bash
cd appointocare-backend
flask --app run.py db revision --autogenerate -m "Description of your changes"
flask --app run.py db upgrade
```

## Seeding Sample Data

The `sample_data.py` script creates large test datasets. **Warning:** It clears existing tables, so use only in development:

```bash
cd appointocare-backend
python sample_data.py
```

## Running Tests

```bash
cd appointocare-backend
python -m unittest discover -s tests -v
```

## Monitoring and Logging

Celery worker logs are visible in the Celery container:

```bash
docker compose logs -f celery
```

Backend API logs are available from the backend container:

```bash
docker compose logs -f backend
```

---

# Support and Contributing

For issues, suggestions, or contributions, please refer to the GitHub repository:
https://github.com/vjamalpure/AppointoCare

---

**Last Updated**: 2024
