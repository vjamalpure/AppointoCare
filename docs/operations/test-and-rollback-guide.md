# AppointoCare — Operations, Testing & Rollback Guide

**Operational Guide for Solo Developer & Pilot Deployment**  
**Date:** October 12, 2026  

---

## 1. Startup & Service Execution

AppointoCare runs as a containerized stack managed via Docker Compose.

### Starting the Stack
```powershell
docker compose up -d
```

### Checking Container Health
```powershell
docker ps
```
All containers should report `Up` and `healthy`:
- `appointocare-frontend-1` on port 4200
- `appointocare-backend-1` on port 8000
- `appointocare-celery-1`
- `appointocare-db-1` on port 5432
- `appointocare-redis-1` on port 6379

### Viewing Application Logs
```powershell
docker compose logs -f backend
docker compose logs -f celery
```

---

## 2. Test Execution Procedures

### A. Full Industry E2E Verification (216 Test Cases)
Tests SuperAdmin, all 9 industry verticals, login, CRUD appointments, services, customers, notifications, industry records, and staff accounts:
```powershell
$env:PYTHONIOENCODING='utf-8'
python "C:\Users\Vivek Jamalpure\.gemini\antigravity-ide\brain\40e058bb-154c-4731-9740-e7b30565d466\scratch\full_industry_verification.py"
```

### B. Internal Backend Audit Tests (191 Test Cases)
Tests all routes, sector templates, token issuance, addons, and role validations directly inside the container:
```powershell
docker exec appointocare-backend-1 python test_audit.py
```

### C. Provider & Migration Integration Tests
```powershell
docker exec appointocare-backend-1 pytest tests/
```

---

## 3. Database Migration & Rollback Procedure

### Safe Migration Policy
- **Never** run `DROP TABLE` or destructive resets against existing pilot data.
- **Never** modify live migrations in place; always generate new sequential Alembic migrations.

### Generating a New Migration
```powershell
docker exec appointocare-backend-1 flask db migrate -m "add_column_name"
```

### Applying Migrations
```powershell
docker exec appointocare-backend-1 flask db upgrade
```

### Rolling Back the Last Migration
```powershell
docker exec appointocare-backend-1 flask db downgrade
```

---

## 4. Code Change Rollback & Git Strategy

1. Before starting a milestone increment, verify working tree is clean:
   ```powershell
   git status
   ```
2. In case of regression or unexpected defect, revert changes safely:
   ```powershell
   git checkout -- <file>
   ```
3. If an applied Git commit must be undone without modifying history:
   ```powershell
   git revert <commit-hash>
   ```

---

## 5. Emergency Database Backup & Recovery

### Immediate Snapshot
```powershell
docker exec appointocare-db-1 pg_dump -U postgres appointocare > backup_appointocare_$(Get-Date -Format 'yyyyMMdd_HHmm').sql
```

### Restoring from Snapshot
```powershell
cat backup_appointocare_YYYYMMDD_HHmm.sql | docker exec -i appointocare-db-1 psql -U postgres -d appointocare
```
