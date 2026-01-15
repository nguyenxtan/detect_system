#!/bin/bash

# Start All Services Manually (No Docker)

echo "Starting Defect System Services..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Function to open new terminal and run command
open_terminal() {
    local title=$1
    local command=$2

    osascript <<EOF
tell application "Terminal"
    do script "cd $(pwd) && echo '=== $title ===' && $command"
    activate
end tell
EOF
}

# 1. Start Backend
echo "Starting Backend..."
open_terminal "Backend API" "cd backend && python3 -m venv venv 2>/dev/null ; source venv/bin/activate && pip install -q -r requirements.txt && python -m app.main"

# Wait a bit
sleep 2

# 2. Start Frontend
echo "Starting Frontend..."
open_terminal "Frontend" "cd frontend && npm install --silent && npm run dev"

# Wait a bit
sleep 2

# 3. Start Telegram Bot
echo "Starting Telegram Bot..."
open_terminal "Telegram Bot" "cd telegram_bot && python3 -m venv venv 2>/dev/null ; source venv/bin/activate && pip install -q -r requirements.txt && python bot.py"

echo ""
echo "✓ All services starting in new terminal windows"
echo ""
echo "Wait 10-20 seconds, then access:"
echo "  Frontend:  http://localhost:3001"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Login: admin / admin123"
