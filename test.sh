#!/bin/bash

# Test Script for Defect Recognition System
# Author: Claude Code

echo "=================================="
echo "  Defect System - Test Script"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo ""
echo "1. Checking prerequisites..."

if command_exists docker; then
    echo -e "${GREEN}✓${NC} Docker installed"
else
    echo -e "${RED}✗${NC} Docker not found"
fi

if command_exists docker-compose; then
    echo -e "${GREEN}✓${NC} Docker Compose installed"
else
    echo -e "${RED}✗${NC} Docker Compose not found"
fi

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python installed: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python3 not found"
fi

if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js installed: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found"
fi

# Create .env if not exists
echo ""
echo "2. Setting up environment..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Create data directories
mkdir -p data/uploads data/reference_images
echo -e "${GREEN}✓${NC} Data directories created"

# Start services with Docker
echo ""
echo "3. Starting services with Docker..."
echo -e "${YELLOW}This may take a few minutes on first run (downloading images)...${NC}"

# Use 'docker compose' (new syntax) instead of 'docker-compose'
docker compose up -d

# Wait for services to be ready
echo ""
echo "4. Waiting for services to start..."
sleep 10

# Check services status
echo ""
echo "5. Checking services status..."
docker compose ps

# Test endpoints
echo ""
echo "6. Testing endpoints..."

# Test Backend Health
echo -n "Testing Backend Health: "
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} (http://localhost:8000/health)"
else
    echo -e "${RED}✗ FAILED${NC} (Status: $HEALTH_RESPONSE)"
fi

# Test Backend Root
echo -n "Testing Backend Root: "
ROOT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$ROOT_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} (http://localhost:8000/)"
else
    echo -e "${RED}✗ FAILED${NC} (Status: $ROOT_RESPONSE)"
fi

# Test Frontend
echo -n "Testing Frontend: "
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} (http://localhost:3001/)"
else
    echo -e "${RED}✗ FAILED${NC} (Status: $FRONTEND_RESPONSE)"
fi

# Show logs
echo ""
echo "7. Recent logs (last 20 lines)..."
echo -e "${YELLOW}=== Backend Logs ===${NC}"
docker compose logs --tail=20 backend

echo ""
echo -e "${YELLOW}=== Telegram Bot Logs ===${NC}"
docker compose logs --tail=20 telegram_bot

# Summary
echo ""
echo "=================================="
echo "  Test Summary"
echo "=================================="
echo ""
echo -e "${GREEN}Services URLs:${NC}"
echo "  Frontend:     http://localhost:3001"
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  PostgreSQL:   localhost:5434"
echo ""
echo -e "${GREEN}Default Login:${NC}"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:        docker compose logs -f"
echo "  Stop services:    docker compose down"
echo "  Restart services: docker compose restart"
echo "  Check status:     docker compose ps"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Open browser: http://localhost:3001"
echo "  2. Login with admin/admin123"
echo "  3. Create a defect profile"
echo "  4. Test Telegram bot"
echo ""
echo "=================================="
