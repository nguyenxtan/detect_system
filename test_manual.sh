#!/bin/bash

# Manual Test Script (No Docker Required)
# For systems without Docker

echo "=================================="
echo "  Manual Test Script"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if backend is running
echo ""
echo "1. Checking Backend..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
if [ "$BACKEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Backend is running${NC} (http://localhost:8000)"
else
    echo -e "${YELLOW}⚠ Backend not running${NC}"
    echo "Start backend with:"
    echo "  cd backend && python -m app.main"
fi

# Check if frontend is running
echo ""
echo "2. Checking Frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/ 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is running${NC} (http://localhost:3001)"
else
    echo -e "${YELLOW}⚠ Frontend not running${NC}"
    echo "Start frontend with:"
    echo "  cd frontend && npm install && npm run dev"
fi

# Check Python
echo ""
echo "3. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python3 not found${NC}"
fi

# Check Node
echo ""
echo "4. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found${NC}"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ npm $NPM_VERSION${NC}"
fi

# Summary
echo ""
echo "=================================="
echo "  Quick Start Commands"
echo "=================================="
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  python -m app.main"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm install"
echo "  npm run dev"
echo ""
echo "Terminal 3 - Telegram Bot:"
echo "  cd telegram_bot"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  python bot.py"
echo ""
echo "=================================="
echo ""
echo -e "${GREEN}URLs:${NC}"
echo "  Frontend:  http://localhost:3001"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo -e "${GREEN}Login:${NC}"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
