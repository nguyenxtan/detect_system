#!/bin/bash
# ========================================
# Deploy Script for Defect System
# ========================================

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create .env from .env.production.example${NC}"
    echo "cp .env.production.example .env"
    echo "Then edit .env with your production values"
    exit 1
fi

# Check required environment variables
echo "🔍 Checking environment variables..."
required_vars=("DATABASE_PASSWORD" "API_SECRET_KEY" "TELEGRAM_BOT_TOKEN" "CORS_ORIGINS")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=.*CHANGE.*" .env || grep -q "^${var}=.*YOUR.*" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}❌ Error: The following variables need to be configured in .env:${NC}"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

echo -e "${GREEN}✅ Environment variables OK${NC}"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/uploads data/reference_images

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
echo "📥 Pulling base images..."
docker-compose -f docker-compose.prod.yml pull

# Build and start containers
echo "🔨 Building containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check container status
echo "🔍 Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# Check backend health
echo "🏥 Checking backend health..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "Waiting for backend... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ Backend health check failed!${NC}"
    echo "Check logs with: docker-compose -f docker-compose.prod.yml logs backend"
    exit 1
fi

# Show logs
echo ""
echo "📋 Recent logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "📊 Useful commands:"
echo "  View logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop:         docker-compose -f docker-compose.prod.yml down"
echo "  Restart:      docker-compose -f docker-compose.prod.yml restart"
echo "  Status:       docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "🔗 Services:"
echo "  Frontend: http://localhost:3001"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "  1. Setup nginx reverse proxy"
echo "  2. Setup SSL certificate with certbot"
echo "  3. Configure firewall (ufw)"
echo "  4. Create admin user"
echo "  5. Setup backup cron job"
echo ""
echo "See DEPLOYMENT.md for detailed instructions"
