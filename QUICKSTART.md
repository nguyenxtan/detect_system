# Quick Start Guide

## For Local Development

### 1. Clone và cài đặt

```bash
git clone https://github.com/nguyenxtan/detect_system.git
cd detect_system
```

### 2. Chạy với Docker (Khuyến nghị)

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Truy cập:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Telegram Bot: Tự động chạy

**Login:**
- Username: `admin`
- Password: `admin123`

### 3. Chạy Manual (Không dùng Docker)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env
python -m app.main
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Telegram Bot:**
```bash
cd telegram_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env with TELEGRAM_BOT_TOKEN
python bot.py
```

## Deploy lên VPS

### Cách 1: Sử dụng PostgreSQL có sẵn trên VPS

```bash
# 1. SSH vào VPS
ssh root@your_vps_ip

# 2. Chạy database script
psql -U postgres -d your_database -f scripts/init_database.sql

# 3. Update .env với database credentials
nano .env

# 4. Start backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 5. Start telegram bot
cd telegram_bot
python bot.py
```

### Cách 2: Deploy toàn bộ với Docker

```bash
# 1. Copy project lên VPS
scp -r detect_system root@your_vps_ip:/root/

# 2. SSH vào VPS
ssh root@your_vps_ip
cd /root/detect_system

# 3. Update .env
nano .env

# 4. Start services
docker-compose up -d

# 5. Check logs
docker-compose logs -f
```

## Sử dụng

### 1. Tạo Defect Profile (Admin)

1. Login vào http://localhost:3001
2. Chọn "Thêm Defect Profile"
3. Điền thông tin:
   - Khách hàng: FAPV
   - Mã SP: GD3346
   - Tên SP: Grommet
   - Loại: can / rach / nhan / phong / ok
   - Mô tả QC
   - Keywords
   - Upload ảnh tham khảo
4. Submit → AI tự động tạo embeddings

### 2. Dùng Telegram Bot

1. Mở Telegram, tìm bot của bạn
2. Gửi `/start`
3. Gửi ảnh khuyết tật
4. Nhận kết quả:
   - Loại khuyết tật
   - Mô tả QC chuẩn
   - Ảnh tham khảo
   - % độ tin cậy

### 3. Xem lịch sử

- Web: "Lịch Sử Báo Cáo"
- Telegram: `/history`

## Troubleshooting

### Backend không start được

```bash
# Check logs
docker-compose logs backend

# Hoặc
cd backend
python -m app.main
```

**Lỗi thường gặp:**
- Database chưa ready → Đợi vài giây
- Port bị chiếm → Đổi port trong docker-compose.yml
- Missing .env → Copy từ .env.example

### Frontend không load

```bash
# Test backend
curl http://localhost:8000/health

# Rebuild
docker-compose up --build frontend
```

### Telegram Bot không phản hồi

```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Test manually
cd telegram_bot
python bot.py
```

## Ports

- **5434**: PostgreSQL
- **8000**: Backend API
- **3001**: Frontend
- **Bot**: Không cần port (polling mode)

## Cấu trúc thư mục

```
detect_system/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── telegram_bot/     # Telegram bot
├── scripts/          # Database scripts
├── data/            # Upload & reference images
├── docker-compose.yml
├── .env.example
└── README.md
```

## Support

- GitHub: https://github.com/nguyenxtan/detect_system
- Email: support@example.com
