# Quick Start - Deploy lên VPS trong 15 phút

## Bước 1: Chuẩn bị VPS (5 phút)

```bash
# SSH vào VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Cài Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
apt install docker-compose -y

# Cài Nginx & Certbot
apt install nginx certbot python3-certbot-nginx ufw git -y
```

## Bước 2: Setup Firewall (2 phút)

```bash
# Enable firewall
ufw allow 22/tcp    # SSH - QUAN TRỌNG!
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
ufw status
```

## Bước 3: Clone và Setup (3 phút)

```bash
# Clone repository
cd /opt
git clone YOUR_REPO_URL defect-system
cd defect-system

# Tạo .env từ template
cp .env.production.example .env

# Generate secrets
echo "DATABASE_PASSWORD=$(openssl rand -base64 32)" >> .env.temp
echo "API_SECRET_KEY=$(openssl rand -hex 32)" >> .env.temp

# Edit .env với nano
nano .env
```

**Trong nano, cập nhật:**
- `DATABASE_PASSWORD`: Copy từ .env.temp
- `API_SECRET_KEY`: Copy từ .env.temp
- `TELEGRAM_BOT_TOKEN`: Token từ @BotFather
- `CORS_ORIGINS`: Domain của bạn (ví dụ: https://defect.yourdomain.com)
- `FRONTEND_API_URL`: Domain của bạn

Ctrl+X, Y, Enter để lưu.

## Bước 4: Deploy Application (3 phút)

```bash
# Chạy deploy script
./deploy.sh

# Tạo admin user
docker exec -it defect_system_backend python3 /app/../scripts/create_admin.py
# Hoặc:
docker-compose -f docker-compose.prod.yml exec backend python3 scripts/create_admin.py
```

## Bước 5: Setup Nginx (2 phút)

```bash
# Copy nginx config
cp nginx.conf.template /etc/nginx/sites-available/defect-system

# Thay YOURDOMAIN.COM bằng domain thật
sed -i 's/YOURDOMAIN.COM/YOUR_ACTUAL_DOMAIN/g' /etc/nginx/sites-available/defect-system

# Enable site
ln -s /etc/nginx/sites-available/defect-system /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## Bước 6: Setup SSL (2 phút)

```bash
# Tạo SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
certbot renew --dry-run
```

## ✅ Xong! Kiểm tra:

1. **Frontend**: https://your-domain.com
2. **API Docs**: https://your-domain.com/docs
3. **Health**: https://your-domain.com/health

---

## 🔧 Troubleshooting

### Không truy cập được web:
```bash
# Check containers
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check nginx
nginx -t
systemctl status nginx
tail -f /var/log/nginx/error.log
```

### Database connection error:
```bash
# Restart database
docker-compose -f docker-compose.prod.yml restart db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db
```

### 502 Bad Gateway:
```bash
# Check backend health
curl http://localhost:8000/health

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📊 Monitoring

```bash
# Xem logs realtime
docker-compose -f docker-compose.prod.yml logs -f

# Xem resource usage
docker stats

# Xem disk usage
df -h
du -sh data/
```

---

## 🔄 Update Code

```bash
cd /opt/defect-system
git pull
./deploy.sh
```

---

## 💾 Backup (Quan trọng!)

```bash
# Tạo backup script
cat > /root/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker exec defect_system_db pg_dump -U postgres defect_system > $BACKUP_DIR/db_$DATE.sql

# Backup data
cd /opt/defect-system
tar -czf $BACKUP_DIR/data_$DATE.tar.gz data/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /root/backup.sh

# Setup cron (chạy mỗi ngày lúc 2h sáng)
crontab -e
# Thêm dòng:
0 2 * * * /root/backup.sh >> /root/backup.log 2>&1
```

---

## 🎯 Checklist Hoàn Tất

- [ ] VPS có Docker & Docker Compose
- [ ] Firewall đã setup (SSH, HTTP, HTTPS)
- [ ] .env đã tạo với values production
- [ ] Application đã deploy thành công
- [ ] Admin user đã tạo
- [ ] Nginx đã cấu hình
- [ ] SSL certificate đã setup
- [ ] Web truy cập được qua HTTPS
- [ ] Backup cron job đã setup
- [ ] Đã test restore từ backup

---

## 📚 Xem thêm

Chi tiết đầy đủ: [DEPLOYMENT.md](./DEPLOYMENT.md)
