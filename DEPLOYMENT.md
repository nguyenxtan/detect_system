# Hướng Dẫn Deploy Lên VPS

## ⚠️ CẢNH BÁO BẢO MẬT - PHẢI FIX TRƯỚC KHI DEPLOY

### 🔴 CÁC VẤN ĐỀ NGHIÊM TRỌNG HIỆN TẠI:

1. **CORS đang allow all origins** (`allow_origins=["*"]`) - Rất nguy hiểm!
2. **Hardcoded credentials** trong docker-compose.yml
3. **Telegram Bot Token** đang public trong code
4. **API Secret Key** yếu và hardcoded
5. **Database password** đơn giản (`postgres123`)

---

## 📋 CHECKLIST DEPLOY LÊN VPS

### 1. **Chuẩn Bị VPS**

#### Yêu cầu tối thiểu:
- **RAM**: 4GB (khuyến nghị 8GB cho AI model)
- **CPU**: 2 cores (khuyến nghị 4 cores)
- **Disk**: 40GB SSD (có thể mở rộng cho database)
- **OS**: Ubuntu 22.04 LTS (khuyến nghị)

#### Cài đặt cơ bản:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install nginx for reverse proxy
sudo apt install nginx -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Install fail2ban for security
sudo apt install fail2ban -y
```

---

### 2. **Cấu Hình Bảo Mật**

#### A. Tạo file `.env` production:
```bash
# Tạo .env từ example
cp .env.example .env

# Generate secret key mạnh
openssl rand -hex 32
```

#### B. Cập nhật `.env` với giá trị production:
```bash
# Database - ĐỔI MẬT KHẨU MẠNH!
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=defect_system
DATABASE_USER=postgres
DATABASE_PASSWORD=<STRONG_PASSWORD_HERE>  # Dùng password generator!

# API - ĐỔI SECRET KEY!
API_SECRET_KEY=<GENERATED_SECRET_FROM_OPENSSL>
DEBUG=False
ENVIRONMENT=production

# CORS - CHỈ CHO PHÉP DOMAIN CỤ THỂ!
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Telegram Bot - KHÔNG COMMIT VÀO GIT!
TELEGRAM_BOT_TOKEN=<YOUR_ACTUAL_BOT_TOKEN>
```

#### C. Thêm `.env` vào `.gitignore`:
```bash
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

---

### 3. **Sửa Code Bảo Mật**

#### A. Fix CORS trong `backend/app/main.py`:

**THAY ĐỔI TỪ:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ NGUY HIỂM!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**THÀNH:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # ✅ AN TOÀN
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

#### B. Xóa hardcoded credentials trong `docker-compose.yml`

---

### 4. **Tạo docker-compose.prod.yml**

Tôi sẽ tạo file này riêng cho production...

---

### 5. **Setup Nginx Reverse Proxy**

#### A. Tạo file `/etc/nginx/sites-available/defect-system`:
```nginx
# HTTP - redirect to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Certbot verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Main configuration
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase upload size for images
        client_max_body_size 20M;
    }

    # Static files (images)
    location /references {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### B. Enable site và restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/defect-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 6. **Setup SSL với Let's Encrypt**

```bash
# Tạo SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

### 7. **Setup Firewall**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (QUAN TRỌNG - không là bị khóa!)
sudo ufw allow 22/tcp

# Allow HTTP và HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status

# ❌ KHÔNG expose database port ra ngoài!
# ❌ KHÔNG expose backend port 8000 ra ngoài!
```

---

### 8. **Deploy Application**

```bash
# 1. Clone repo lên VPS
git clone <your-repo-url>
cd detect_system

# 2. Tạo .env file (QUAN TRỌNG!)
nano .env
# Copy nội dung từ section 2B

# 3. Tạo thư mục data
mkdir -p data/uploads data/reference_images

# 4. Build và start containers
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Check logs
docker-compose logs -f

# 6. Tạo admin user đầu tiên
docker exec -it defect_system_backend python3 -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = User(
    username='admin',
    hashed_password=get_password_hash('your-secure-password'),
    full_name='Admin User',
    role='admin',
    is_active=True
)
db.add(user)
db.commit()
print('Admin user created!')
"
```

---

### 9. **Data Backup Strategy**

```bash
# Tạo script backup database
cat > /home/youruser/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/youruser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec defect_system_db pg_dump -U postgres defect_system > $BACKUP_DIR/db_$DATE.sql

# Backup uploaded images
tar -czf $BACKUP_DIR/data_$DATE.tar.gz data/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /home/youruser/backup-db.sh

# Setup cron job (chạy mỗi ngày lúc 2h sáng)
crontab -e
# Thêm dòng:
0 2 * * * /home/youruser/backup-db.sh >> /home/youruser/backup.log 2>&1
```

---

### 10. **Monitoring và Logging**

```bash
# Cài đặt log rotation
sudo nano /etc/logrotate.d/docker-containers

# Thêm nội dung:
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size=10M
  missingok
  delaycompress
  copytruncate
}

# Setup monitoring với Docker stats
docker stats --no-stream > /home/youruser/docker-stats.log
```

---

### 11. **Environment Variables cho Frontend**

Update `frontend/Dockerfile` để pass environment variables:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Build với production API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build với production URL:
```bash
docker-compose -f docker-compose.prod.yml build --build-arg VITE_API_URL=https://yourdomain.com
```

---

### 12. **Health Checks và Auto-restart**

Containers đã có `restart: unless-stopped`, nhưng nên thêm health checks:

```yaml
# Trong docker-compose.prod.yml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

---

## 🚨 CHECKLIST TRƯỚC KHI GO LIVE

- [ ] Đã đổi tất cả passwords mạnh
- [ ] Đã đổi API_SECRET_KEY
- [ ] Đã fix CORS chỉ cho phép domain cụ thể
- [ ] Đã xóa Telegram Bot Token khỏi code
- [ ] Đã thêm .env vào .gitignore
- [ ] Đã setup SSL certificate
- [ ] Đã setup firewall
- [ ] Đã setup backup tự động
- [ ] Đã test restore từ backup
- [ ] Đã tạo admin user đầu tiên
- [ ] Đã test đầy đủ chức năng trên production
- [ ] Đã setup monitoring/alerts

---

## 🔧 Troubleshooting

### Database connection errors:
```bash
docker-compose logs db
docker-compose logs backend
```

### Frontend không connect được backend:
```bash
# Check CORS settings
# Check VITE_API_URL trong build
# Check nginx proxy configuration
```

### Out of memory:
```bash
# Check memory usage
free -h
docker stats

# Add swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📞 Support

Nếu gặp vấn đề, check logs:
```bash
docker-compose logs -f --tail=100
sudo tail -f /var/log/nginx/error.log
```
