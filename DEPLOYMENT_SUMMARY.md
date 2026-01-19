# Deployment Configuration Update Summary

## Overview

Updated the detect_system deployment configuration to support frontend deployment on port 3002 without conflicts, with proper production environment setup and aaPanel reverse proxy support.

## Files Created

### 1. `frontend/nginx.conf` (NEW)
Production Nginx configuration for frontend container with:
- SPA routing support (serve index.html for all routes)
- Gzip compression
- Security headers
- Static file caching
- Optional API proxy section (commented out by default for two-domain setup)
- Health check endpoint

## Files Modified

### 1. `frontend/Dockerfile`

**Changes:**
- Added build argument `ARG VITE_API_URL` to accept API URL during build
- Set environment variable `ENV VITE_API_URL` for Vite build process
- Enabled nginx.conf copy (uncommented line 30)
- Added non-root user creation for security

**Diff:**
```diff
FROM node:18-alpine as build

WORKDIR /app

+# Build arguments for API URL
+ARG VITE_API_URL=http://localhost:8000
+
+# Set environment variable for Vite build
+ENV VITE_API_URL=${VITE_API_URL}

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

-# Build the app
+# Build the app with environment variables
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

-# Copy nginx config (optional)
-# COPY nginx.conf /etc/nginx/conf.d/default.conf
+# Copy nginx config
+COPY nginx.conf /etc/nginx/conf.d/default.conf
+
+# Create non-root user for nginx
+RUN addgroup -g 101 -S nginx && \
+    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 2. `docker-compose.prod.yml`

**Changes:**
- Changed frontend port binding from `3001` to `3002`
- Updated build arg from `VITE_API_URL` to use `${FRONTEND_API_URL}` env variable
- Added frontend healthcheck
- Default API URL set to `https://api.ipv.snpdemo.com`

**Diff:**
```diff
# Frontend
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    args:
-     VITE_API_URL: ${FRONTEND_API_URL:-https://yourdomain.com}
+     VITE_API_URL: ${FRONTEND_API_URL:-https://api.ipv.snpdemo.com}
  container_name: defect_system_frontend
  # ❌ CHỈ expose cho nginx reverse proxy
  expose:
    - "80"
  ports:
-   - "127.0.0.1:3001:80"  # Chỉ bind localhost
+   - "127.0.0.1:3002:80"  # Chỉ bind localhost - port 3002 to avoid conflicts
  depends_on:
    backend:
      condition: service_healthy
+ healthcheck:
+   test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:80/health"]
+   interval: 30s
+   timeout: 10s
+   retries: 3
+   start_period: 10s
  restart: unless-stopped
  networks:
    - app-network
  # Security options
  security_opt:
    - no-new-privileges:true
  read_only: true
  tmpfs:
    - /var/cache/nginx:rw,noexec,nosuid
    - /var/run:rw,noexec,nosuid
```

### 3. `.env.production.example`

**Changes:**
- Updated CORS settings with two-domain example
- Renamed `FRONTEND_API_URL` (was `FRONTEND_API_URL`)
- Added comments for both single and two-domain deployment options
- Set default domain to `ipv.snpdemo.com`

**Diff:**
```diff
# CORS - CHỈ CHO PHÉP DOMAIN CỤ THỂ!
# 🔴 ĐỔI THÀNH DOMAIN THẬT CỦA BẠN!
-CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
+# Option 1: Two-domain setup
+CORS_ORIGINS=https://ipv.snpdemo.com,https://api.ipv.snpdemo.com
+# Option 2: Single-domain setup (uncomment if using)
+# CORS_ORIGINS=https://ipv.snpdemo.com

-# Frontend API URL (dùng cho build)
-FRONTEND_API_URL=https://yourdomain.com
+# Frontend API URL (used during build)
+# Option 1: Two-domain setup - frontend calls API domain directly
+FRONTEND_API_URL=https://api.ipv.snpdemo.com
+# Option 2: Single-domain setup - frontend calls /api path (uncomment if using)
+# FRONTEND_API_URL=https://ipv.snpdemo.com
```

## Deployment Architecture

### Port Allocation (VPS)
```
Port 3000: iconic_web UI
Port 3001: license.snpdemo.com
Port 3002: defect_system frontend (NEW) ← 127.0.0.1 only
Port 8000: defect_system backend     ← 127.0.0.1 only
```

### Network Flow (Two-Domain Setup - Recommended)

```
Internet
   │
   │ HTTPS (443)
   ↓
aaPanel Nginx (80/443)
   │
   ├─→ ipv.snpdemo.com
   │      │ SSL Termination
   │      │ Reverse Proxy
   │      ↓
   │   127.0.0.1:3002 (Frontend Container)
   │      │ Nginx serves React SPA
   │      ↓
   │   Browser loads app
   │   Frontend makes API calls to →
   │
   └─→ api.ipv.snpdemo.com
          │ SSL Termination
          │ Reverse Proxy
          ↓
       127.0.0.1:8000 (Backend Container)
          │ FastAPI
          ↓
       db:5432 (PostgreSQL - internal only)
```

### Network Flow (Single-Domain Setup - Alternative)

```
Internet
   │
   │ HTTPS (443)
   ↓
aaPanel Nginx (80/443)
   │
   └─→ ipv.snpdemo.com
          │ SSL Termination
          │ Reverse Proxy
          ↓
       127.0.0.1:3002 (Frontend Container)
          │ Nginx serves:
          │ - / → React SPA
          │ - /api → Proxy to backend:8000
          ↓
       127.0.0.1:8000 (Backend Container)
          │ FastAPI
          ↓
       db:5432 (PostgreSQL - internal only)
```

## Build & Deploy Commands

### On Local Machine (First Time)

```bash
# Commit and push changes
git add .
git commit -m "Add production frontend deployment with aaPanel support"
git push origin main
```

### On VPS

```bash
# Navigate to project directory
cd /root/defect_portal_ivp/detect_system

# Pull latest code
git pull origin main

# Configure environment (first time only)
cp .env.production.example .env
nano .env

# Important: Update these values in .env:
# - DATABASE_PASSWORD=$(openssl rand -base64 32)
# - API_SECRET_KEY=$(openssl rand -hex 32)
# - TELEGRAM_BOT_TOKEN=your_token
# - CORS_ORIGINS=https://ipv.snpdemo.com,https://api.ipv.snpdemo.com
# - FRONTEND_API_URL=https://api.ipv.snpdemo.com

# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check status
docker compose -f docker-compose.prod.yml ps

# Expected output:
# defect_system_db          Up (healthy)
# defect_system_backend     Up (healthy)  127.0.0.1:8000->8000/tcp
# defect_system_frontend    Up (healthy)  127.0.0.1:3002->80/tcp
# defect_system_telegram_bot Up

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Test locally
curl http://127.0.0.1:8000/health    # Backend health
curl http://127.0.0.1:3002/health    # Frontend health
```

## aaPanel Configuration

### Step 1: Create Frontend Site

1. **Website → Add Site**
   - Domain: `ipv.snpdemo.com`
   - PHP: None
   - Database: None

2. **Settings → Reverse Proxy**
   - Target: `http://127.0.0.1:3002`
   - Enable SSL (Let's Encrypt)
   - Force HTTPS

### Step 2: Create Backend Site

1. **Website → Add Site**
   - Domain: `api.ipv.snpdemo.com`
   - PHP: None
   - Database: None

2. **Settings → Reverse Proxy**
   - Target: `http://127.0.0.1:8000`
   - Enable SSL (Let's Encrypt)
   - Force HTTPS
   - Increase timeout to 600s (for AI processing)

### Step 3: Verify

```bash
# Test frontend
curl -I https://ipv.snpdemo.com
# Should return: HTTP/2 200

# Test backend
curl https://api.ipv.snpdemo.com/health
# Should return: {"status":"healthy"}

# Test login via API
curl -X POST https://api.ipv.snpdemo.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# Should return JWT token
```

## Updating After Changes

```bash
# Local machine
git add .
git commit -m "Your changes"
git push origin main

# VPS
cd /root/defect_portal_ivp/detect_system
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build

# Restart only specific service if needed
docker compose -f docker-compose.prod.yml up -d --build frontend
docker compose -f docker-compose.prod.yml up -d --build backend
```

## Security Features

✅ **Network Security**
- Database not exposed to internet
- Backend only accessible via localhost:8000
- Frontend only accessible via localhost:3002
- aaPanel Nginx handles SSL termination
- All external traffic goes through reverse proxy

✅ **Container Security**
- `no-new-privileges:true` on all containers
- Frontend runs in read-only mode
- Minimal capabilities (cap_drop: ALL)
- Non-root user for nginx

✅ **Application Security**
- CORS restricted to specific domains
- Strong password requirements
- JWT token authentication
- Secrets via environment variables (not hardcoded)

## Troubleshooting

### Frontend shows blank page
```bash
# Check browser console (F12)
# Common issues:
# 1. API URL mismatch - verify VITE_API_URL in build
# 2. CORS error - check CORS_ORIGINS in backend .env

# Rebuild with correct API URL
docker compose -f docker-compose.prod.yml up -d --build frontend
```

### API CORS errors
```bash
# Verify backend CORS settings
docker compose -f docker-compose.prod.yml exec backend env | grep CORS

# Should show:
# CORS_ORIGINS=https://ipv.snpdemo.com,https://api.ipv.snpdemo.com

# Update .env and restart
docker compose -f docker-compose.prod.yml restart backend
```

### Container won't start
```bash
# View logs
docker compose -f docker-compose.prod.yml logs <service_name>

# Common fixes:
# - Port conflict: Change port in docker-compose.prod.yml
# - Build error: Check Dockerfile syntax
# - Dependency error: Wait for dependent service to be healthy
```

## Documentation References

- Detailed deployment guide: [DEPLOY_AAPANEL.md](DEPLOY_AAPANEL.md)
- Main README: [README.md](README.md)
- Environment variables: `.env.production.example`

---

**Configuration Type:** Production with aaPanel
**Last Updated:** 2026-01-19
**Deployment Target:** VPS at /root/defect_portal_ivp/detect_system
