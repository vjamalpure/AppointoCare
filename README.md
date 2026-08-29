# AppointoCare

AppointoCare is an appointment and organization management application with an Angular frontend, Flask REST API, PostgreSQL database, Redis, and a Celery worker.

## Project layout

- `appointocore-frontend/`: Angular 18 application served by Nginx in production.
- `appointocore-backend/`: Flask API, SQLAlchemy models, Alembic migrations, and Celery tasks.
- `docker-compose.yml`: Local container orchestration for PostgreSQL, Redis, Flask, Celery, and Nginx.

## Run with Docker Compose

Prerequisites: Docker Desktop with Compose enabled.

1. Optional: copy `.env.example` to `.env` for explicit local settings. Compose also supplies these development defaults automatically.
2. Start the full stack:

   ```bash
   docker compose up --build
   ```

3. Open the application at `http://localhost:4200`.
4. The API is available at `http://localhost:8000`.
5. Stop the stack with `Ctrl+C`, or run:

   ```bash
   docker compose down
   ```

PostgreSQL data is stored in the `postgres_data` Docker volume. To remove the database volume as well:

```bash
docker compose down -v
```

The backend waits for PostgreSQL and Redis, runs `flask db upgrade`, initializes demo data if `SEED_DEMO_DATA=true`, and then starts Gunicorn. The Celery worker starts after the backend is healthy. PostgreSQL data persists in the `postgres_data` volume, so the migration and seed are safe to run every time the containers start.

### Demo logins

With the default development Compose settings:

| Role | Organization code | Username | Password |
| --- | --- | --- | --- |
| Super Admin | leave blank | `superadmin` | `Admin@12345` |
| Organization Admin | `ORG1` | `org1` | `Org@12345` |
| Organization Staff | `ORG1` | `staff1` | `Staff@12345` |

The seed is idempotent: existing accounts and records are skipped. Set `SEED_DEMO_DATA=false` for an empty database or production deployment.

### Versioned platform APIs

The platform endpoints are available under `/api/v1/platform`:

- `GET/POST /plans`: Super Admin subscription plan management.
- `GET/POST /templates`: sector service templates; creation is restricted to Super Admin.
- `GET/POST /campaigns`: organization-scoped campaign drafts and scheduling metadata.
- `GET /notifications` and `POST /notifications/{id}/read`: organization notifications.
- `GET/POST /branches`: organization-scoped branches.
- `GET /reports/summary`: tenant-scoped KPI summary, or an optional organization filter for Admin.

All tenant endpoints derive `organization_id` from the JWT claims. They do not trust a client-supplied organization ID.

### Provider integrations

Provider adapters live under `appointocore-backend/app/providers` and application services use those adapters instead of vendor SDKs. Development defaults to mock providers; production does not fall back to mocks. Configure a real provider only through environment variables:

- `GET /api/v1/providers/status`: authenticated provider state inspection.
- `POST /api/v1/providers/payments/orders`: create a payment order.
- `POST /api/v1/providers/payments/verify`: verify a payment signature.
- `POST /api/v1/providers/webhooks/razorpay`: signed, idempotent Razorpay webhook endpoint.
- `GET/POST /api/v1/providers/webhooks/whatsapp`: Meta webhook verification and signed event intake.

Without credentials, real-provider operations return a controlled provider configuration error. Mock operations are intended for development and automated tests only. Webhook endpoints never log access tokens or raw provider secrets.

## Run locally

### Backend

Prerequisites: Python 3.12+, PostgreSQL, and Redis.

```bash
cd appointocore-backend
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create or update `appointocore-backend/.env` with local values. The database URL must point to your local PostgreSQL instance, for example:

```dotenv
SECRET_KEY=local-secret
JWT_SECRET_KEY=local-jwt-secret
DATABASE_URL=postgresql://postgres:password@localhost:5432/appointocore
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

Create the database, apply migrations, and start the API:

```bash
flask --app run.py db upgrade
python run.py
```

For local PostgreSQL, use `postgresql://` with the PostgreSQL host, port, database, username, and password. Do not use the Docker hostname `db` from a process running directly on Windows; use `localhost` instead.

In another terminal, start the worker from `appointocore-backend`:

```bash
.\venv\Scripts\Activate.ps1
celery -A celery_worker.celery worker --loglevel=info
```

To create initial users locally, set `ADMIN_PASSWORD` and `ORG_PASSWORD` in the backend environment and run:

```bash
python create_users.py
```

The `sample_data.py` script is for disposable development databases only because it clears existing tables:

```bash
python sample_data.py
```

### Frontend

Prerequisites: Node.js 20+ and npm.

```bash
cd appointocore-frontend
npm ci
npm start
```

Open `http://localhost:4200`. The local Angular environment targets `http://localhost:8000`; update `src/environments/environment.ts` if your API uses another URL.

Build and test the frontend with:

```bash
npm run build
npm test
```

## Configuration notes

- Do not use the example secrets in production.
- Compose uses `db` and `redis` as service hostnames. Local development uses `localhost`.
- If a PostgreSQL password contains URL-reserved characters, URL-encode it before putting it in `DATABASE_URL`.
- The frontend production image includes an Nginx fallback to `index.html`, so Angular client-side routes work on direct navigation.
