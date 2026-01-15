#!/bin/bash

echo "Rebuilding Defect System..."

# Stop all services
echo "1. Stopping services..."
docker compose down

# Rebuild backend (with fix)
echo "2. Rebuilding backend..."
docker compose build --no-cache backend

# Start all services
echo "3. Starting all services..."
docker compose up -d

# Wait for services
echo "4. Waiting for services to start..."
sleep 15

# Check status
echo "5. Checking status..."
docker compose ps

# Test endpoints
echo ""
echo "6. Testing endpoints..."
echo -n "Backend: "
curl -s http://localhost:8000/health | grep -q healthy && echo "✓ OK" || echo "✗ FAILED"

echo -n "Frontend: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/ | grep -q 200 && echo "✓ OK" || echo "✗ FAILED"

echo ""
echo "Done! Access at:"
echo "  Frontend: http://localhost:3001"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "View logs: docker compose logs -f"
