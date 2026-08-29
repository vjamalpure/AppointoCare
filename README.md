# AppointoCare

AppointoCare is an appointment and organization management application with an Angular frontend, Flask REST API, PostgreSQL database, Redis, and a Celery worker.

## Project layout

- `appointocore-frontend/`: Angular 18 application served by Nginx in production.
- `appointocore-backend/`: Flask API, SQLAlchemy models, Alembic migrations, and Celery tasks.
- `docker-compose.yml`: Local container orchestration for PostgreSQL, Redis, Flask, Celery, and Nginx.

## Run with Docker Compose

Prerequisites: Docker Desktop with Compose enabled.

1. Copy `.env.example` to `.env` in this directory and replace the secrets for anything beyond local development.
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

The backend waits for PostgreSQL and Redis, runs `flask db upgrade`, and then starts Gunicorn. The Celery worker starts after the backend is healthy.

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
