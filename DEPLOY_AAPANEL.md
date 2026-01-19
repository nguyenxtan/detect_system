# aaPanel Deployment Guide - Defect System

This guide explains how to deploy the Defect System on a VPS with aaPanel.

## Prerequisites

- VPS with Docker and Docker Compose installed
- aaPanel installed and configured
- Domains pointed to your VPS:
  - `ipv.snpdemo.com` (for frontend UI)
  - `api.ipv.snpdemo.com` (for backend API)

## Current Port Usage

- Port 3000: iconic_web UI
- Port 3001: license.snpdemo.com
- Port 3002: defect_system frontend (NEW)
- Port 8000: defect_system backend API

## Deployment Steps

### 1. Clone Repository on VPS

```bash
cd /root/defect_portal_ivp
git clone https://github.com/yourusername/detect_system.git
cd detect_system
```

### 2. Configure Environment Variables

Copy and edit the production environment file:

```bash
cp .env.production.example .env
nano .env
```

**Important settings to update:**

```bash
# Strong database password
DATABASE_PASSWORD=$(openssl rand -base64 32)

# Strong API secret key
API_SECRET_KEY=$(openssl rand -hex 32)

# Telegram bot token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# CORS - Allow your domains
CORS_ORIGINS=https://ipv.snpdemo.com,https://api.ipv.snpdemo.com

# Frontend API URL - must match your API domain
FRONTEND_API_URL=https://api.ipv.snpdemo.com
```

### 3. Build and Start Services

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs if needed
docker compose -f docker-compose.prod.yml logs -f
```

Expected services:
- ✅ defect_system_db (PostgreSQL) - internal only
- ✅ defect_system_backend - listening on 127.0.0.1:8000
- ✅ defect_system_frontend - listening on 127.0.0.1:3002
- ✅ defect_system_telegram_bot - no exposed ports

### 4. Create Admin User

```bash
docker compose -f docker-compose.prod.yml exec backend python3 -c "
from app.core.database import SessionLocal, engine
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Drop existing tables if needed
User.__table__.drop(engine, checkfirst=True)
User.__table__.create(engine)

db = SessionLocal()
try:
    admin = User(
        username='admin',
        email='admin@defect-system.com',
        hashed_password=pwd_context.hash('admin123'),
        full_name='System Administrator',
        role='admin',
        is_active=True
    )
    db.add(admin)
    db.commit()
    print('✅ Admin user created: username=admin, password=admin123')
except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()
finally:
    db.close()
"
```

### 5. Test Services Locally

```bash
# Test backend health
curl http://127.0.0.1:8000/health

# Test backend login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test frontend health
curl http://127.0.0.1:3002/health
```

## aaPanel Configuration

### Option 1: Two-Domain Setup (Recommended)

This setup uses separate domains for frontend and API.

#### Frontend: ipv.snpdemo.com

1. **Create Website in aaPanel**
   - Go to: Website → Add site
   - Domain: `ipv.snpdemo.com`
   - Document root: `/www/wwwroot/ipv.snpdemo.com` (not used, just placeholder)
   - PHP: None
   - Database: None

2. **Configure Reverse Proxy**
   - Click website → Settings → Reverse Proxy
   - Add Proxy:
     - Proxy name: `defect_frontend`
     - Target URL: `http://127.0.0.1:3002`
     - Enable cache: No
     - Custom config:

```nginx
location / {
    proxy_pass http://127.0.0.1:3002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

3. **Enable SSL**
   - Click website → SSL
   - Select Let's Encrypt
   - Apply for certificate
   - Force HTTPS: Enable

#### API: api.ipv.snpdemo.com

1. **Create Website in aaPanel**
   - Go to: Website → Add site
   - Domain: `api.ipv.snpdemo.com`
   - Document root: `/www/wwwroot/api.ipv.snpdemo.com` (not used)
   - PHP: None
   - Database: None

2. **Configure Reverse Proxy**
   - Click website → Settings → Reverse Proxy
   - Add Proxy:
     - Proxy name: `defect_backend`
     - Target URL: `http://127.0.0.1:8000`
     - Custom config:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;

    # Increase timeout for AI processing
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
}
```

3. **Enable SSL**
   - Click website → SSL
   - Select Let's Encrypt
   - Apply for certificate
   - Force HTTPS: Enable

### Option 2: Single-Domain Setup (Alternative)

This setup uses one domain with `/api` path for backend.

#### 1. Update Environment Variables

Edit `.env` on VPS:

```bash
# Use single domain for CORS
CORS_ORIGINS=https://ipv.snpdemo.com

# Frontend calls /api path
FRONTEND_API_URL=https://ipv.snpdemo.com
```

#### 2. Update Frontend Nginx Config

Edit `frontend/nginx.conf` and uncomment the API proxy section:

```nginx
# Uncomment this section:
location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

#### 3. Rebuild Frontend

```bash
docker compose -f docker-compose.prod.yml up -d --build frontend
```

#### 4. Configure aaPanel

Only configure `ipv.snpdemo.com` with reverse proxy to `http://127.0.0.1:3002`.

## Post-Deployment Verification

### 1. Test Frontend

Visit: `https://ipv.snpdemo.com`

- Should load the login page
- Check browser console for errors

### 2. Test API

Visit: `https://api.ipv.snpdemo.com/docs` (or `https://ipv.snpdemo.com/api/docs` for single-domain)

- Should show FastAPI Swagger UI

### 3. Test Login

1. Open frontend: `https://ipv.snpdemo.com`
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. Should successfully log in and redirect to dashboard

### 4. Check CORS

Open browser console (F12) and verify no CORS errors.

## Updating After Code Changes

```bash
# On local machine - commit and push changes
git add .
git commit -m "Your changes"
git push origin main

# On VPS - pull and rebuild
cd /root/defect_portal_ivp/detect_system
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Frontend shows "Network Error"

Check:
1. Browser console for exact error
2. Verify `FRONTEND_API_URL` in `.env` matches your API domain
3. Check CORS settings in backend `.env`

```bash
# View backend logs
docker compose -f docker-compose.prod.yml logs backend

# Check CORS is set correctly
docker compose -f docker-compose.prod.yml exec backend env | grep CORS
```

### API returns 502 Bad Gateway

Check:
1. Backend is running: `docker compose -f docker-compose.prod.yml ps`
2. Backend health: `curl http://127.0.0.1:8000/health`
3. aaPanel reverse proxy is pointing to correct port

### Frontend container keeps restarting

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs frontend

# Common issues:
# 1. Build failed - check frontend code
# 2. nginx.conf syntax error - verify config
```

### Database connection errors

```bash
# Check database is running
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker compose -f docker-compose.prod.yml logs db

# Verify connection from backend
docker compose -f docker-compose.prod.yml exec backend python3 -c "
from app.core.database import engine
try:
    engine.connect()
    print('✅ Database connection OK')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

## Security Checklist

- ✅ Database not exposed to internet (only `expose`, no public `ports`)
- ✅ Backend only on localhost:8000
- ✅ Frontend only on localhost:3002
- ✅ Strong `DATABASE_PASSWORD` set
- ✅ Strong `API_SECRET_KEY` set
- ✅ CORS restricted to specific domains
- ✅ SSL certificates configured
- ✅ Force HTTPS enabled
- ✅ Default admin password changed (after first login)

## Maintenance Commands

```bash
# View all logs
docker compose -f docker-compose.prod.yml logs -f

# Restart all services
docker compose -f docker-compose.prod.yml restart

# Stop all services
docker compose -f docker-compose.prod.yml down

# Rebuild and restart specific service
docker compose -f docker-compose.prod.yml up -d --build backend

# Clean up old images
docker image prune -a

# Backup database
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres defect_system > backup_$(date +%Y%m%d).sql
```

## Support

For issues, check:
1. Docker logs
2. aaPanel Nginx error logs: `/www/wwwlogs/`
3. Browser console (F12)

---

**Deployment Date:** $(date)
**VPS Location:** /root/defect_portal_ivp/detect_system
**Frontend URL:** https://ipv.snpdemo.com
**API URL:** https://api.ipv.snpdemo.com
