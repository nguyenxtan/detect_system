#!/bin/bash

# Script to deploy new CRUD modules to VPS
# Run this on your VPS: ssh root@ipv.snpdemo.com 'bash -s' < deploy_vps.sh

set -e  # Exit on error

echo "========================================="
echo "Deploying New CRUD Modules to VPS"
echo "========================================="
echo ""

# Navigate to project directory
cd /root/defect_portal_ivp/detect_system

# Step 1: Pull latest code
echo "Step 1: Pulling latest code from GitHub..."
git pull origin main
echo "✓ Code updated"
echo ""

# Step 2: Stop current containers
echo "Step 2: Stopping current containers..."
docker compose -f docker-compose.prod.yml down
echo "✓ Containers stopped"
echo ""

# Step 3: Rebuild images (backend has new dependencies)
echo "Step 3: Rebuilding Docker images..."
docker compose -f docker-compose.prod.yml build --no-cache backend
docker compose -f docker-compose.prod.yml build frontend
echo "✓ Images rebuilt"
echo ""

# Step 4: Start services
echo "Step 4: Starting services..."
docker compose -f docker-compose.prod.yml up -d
echo "✓ Services started"
echo ""

# Step 5: Wait for backend to be ready
echo "Step 5: Waiting for backend to initialize..."
sleep 10
echo "✓ Backend should be ready"
echo ""

# Step 6: Check services status
echo "Step 6: Checking services status..."
docker compose -f docker-compose.prod.yml ps
echo ""

# Step 7: Check backend logs for database creation
echo "Step 7: Checking backend logs (last 30 lines)..."
docker compose -f docker-compose.prod.yml logs backend --tail 30
echo ""

# Step 8: Verify new tables created
echo "Step 8: Verifying new database tables..."
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -d defect_system -c "\dt" | grep -E "(customers|products|defect_types|severity_levels)" || echo "Checking tables..."
echo ""

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Access frontend: https://ipv.snpdemo.com"
echo "2. Login as admin"
echo "3. Check new menu items:"
echo "   - Khách Hàng (Customers)"
echo "   - Sản Phẩm (Products)"
echo "   - Loại Lỗi (Defect Types)"
echo "   - Mức Độ (Severity Levels)"
echo ""
echo "To view logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f backend"
echo ""
echo "To check database:"
echo "  docker compose -f docker-compose.prod.yml exec db psql -U postgres -d defect_system"
echo ""
