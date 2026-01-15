# Commands Cheat Sheet

## 🚀 Quick Start (Cách Nhanh Nhất)

```bash
# Tự động test tất cả
./test.sh
```

**Hoặc thủ công:**

```bash
# 1. Copy env
cp .env.example .env

# 2. Start
docker-compose up -d

# 3. Check
docker-compose ps

# 4. Open browser
open http://localhost:3001
```

Login: `admin` / `admin123`

---

## 🐳 Docker Commands

### Start/Stop

```bash
# Start tất cả
docker-compose up -d

# Start và xem logs
docker-compose up

# Stop tất cả
docker-compose down

# Stop và xóa volumes
docker-compose down -v

# Restart
docker-compose restart

# Restart 1 service
docker-compose restart backend
```

### Logs & Debug

```bash
# Xem logs tất cả
docker-compose logs -f

# Logs 1 service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f telegram_bot

# Logs 100 dòng cuối
docker-compose logs --tail=100 backend

# Check status
docker-compose ps

# Exec vào container
docker-compose exec backend bash
docker-compose exec db psql -U postgres -d defect_system
```

### Rebuild

```bash
# Rebuild tất cả
docker-compose build

# Rebuild 1 service
docker-compose build backend

# Rebuild và restart
docker-compose up -d --build

# Force rebuild (không cache)
docker-compose build --no-cache
```

---

## 🔧 Development Commands

### Backend

```bash
cd backend

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python -m app.main

# Run with reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install new package
pip install package_name
pip freeze > requirements.txt
```

### Frontend

```bash
cd frontend

# Setup
npm install

# Run dev
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Install new package
npm install package-name
```

### Telegram Bot

```bash
cd telegram_bot

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python bot.py
```

---

## 🗄️ Database Commands

### Using Docker PostgreSQL

```bash
# Connect to database
docker-compose exec db psql -U postgres -d defect_system

# Backup
docker-compose exec db pg_dump -U postgres defect_system > backup.sql

# Restore
docker-compose exec -T db psql -U postgres -d defect_system < backup.sql

# Run SQL file
docker-compose exec -T db psql -U postgres -d defect_system < scripts/init_database.sql
```

### SQL Queries

```sql
-- List tables
\dt

-- Describe table
\d users
\d defect_profiles
\d defect_incidents

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM defect_profiles;
SELECT COUNT(*) FROM defect_incidents;

-- List users
SELECT id, username, email, role FROM users;

-- List defect profiles
SELECT id, customer, part_code, defect_type, defect_title FROM defect_profiles;

-- Recent incidents
SELECT * FROM defect_incidents ORDER BY created_at DESC LIMIT 10;
```

---

## 🧪 Testing Commands

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get defect profiles (need token)
curl http://localhost:8000/api/defects/profiles \
  -H "Authorization: Bearer YOUR_TOKEN"

# API Documentation
open http://localhost:8000/docs
```

### Frontend Tests

```bash
# Open in browser
open http://localhost:3001

# Test build
cd frontend
npm run build
npm run preview
```

---

## 📊 Monitoring

```bash
# Docker stats
docker stats

# Disk usage
docker system df

# Container resources
docker-compose top

# Network
docker network ls
docker network inspect detect_system_default
```

---

## 🧹 Cleanup

```bash
# Stop và xóa containers
docker-compose down

# Xóa containers + volumes
docker-compose down -v

# Xóa containers + volumes + images
docker-compose down -v --rmi all

# Clean Docker system
docker system prune -a

# Remove venv (backend)
cd backend
rm -rf venv

# Remove node_modules (frontend)
cd frontend
rm -rf node_modules

# Remove all build artifacts
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name "node_modules" -exec rm -rf {} +
find . -type d -name "venv" -exec rm -rf {} +
```

---

## 🚢 Deployment

### Deploy to VPS

```bash
# 1. Copy to VPS
scp -r detect_system root@your_vps_ip:/root/

# 2. SSH to VPS
ssh root@your_vps_ip
cd /root/detect_system

# 3. Update .env
nano .env

# 4. Start
docker-compose up -d

# 5. Check
docker-compose logs -f
```

### Update Deployment

```bash
# SSH to VPS
ssh root@your_vps_ip
cd /root/detect_system

# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

---

## 🔑 Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'
alias dcr='docker-compose restart'

# Project shortcuts
alias defect-start='cd ~/detect_system && docker-compose up -d'
alias defect-stop='cd ~/detect_system && docker-compose down'
alias defect-logs='cd ~/detect_system && docker-compose logs -f'
alias defect-test='cd ~/detect_system && ./test.sh'
```

---

## 📝 Git Commands

```bash
# Status
git status

# Add all changes
git add .

# Commit
git commit -m "Your message"

# Push
git push origin main

# Pull
git pull origin main

# Create branch
git checkout -b feature/new-feature

# View logs
git log --oneline -10
```

---

## 🆘 Troubleshooting Commands

### Port Conflicts

```bash
# Find process using port
lsof -i :8000
lsof -i :3001
lsof -i :5434

# Kill process
kill -9 <PID>
```

### Reset Everything

```bash
# Stop all
docker-compose down -v

# Remove data
rm -rf data/uploads/*
rm -rf data/reference_images/*

# Rebuild
docker-compose up -d --build

# Re-init database
docker-compose exec -T db psql -U postgres -d defect_system < scripts/init_database.sql
```

### Check Service Health

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3001/

# Database
docker-compose exec db pg_isready -U postgres

# All containers
docker-compose ps
docker inspect <container_id> | grep -i health
```

---

## 📞 Support

- GitHub: https://github.com/nguyenxtan/detect_system
- Issues: https://github.com/nguyenxtan/detect_system/issues
