#!/bin/bash
# Script to run database migration on production

echo "=== Running Database Migration: Add customer_id and product_id to defect_profiles ==="
echo ""

echo "Step 1: Backup database first (IMPORTANT!)"
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres defect_system > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql
echo "✓ Backup created"
echo ""

echo "Step 2: Run migration SQL"
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres defect_system < add_foreign_keys_migration.sql
echo ""

echo "Step 3: Verify migration"
docker compose -f docker-compose.prod.yml exec db psql -U postgres defect_system -c "
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'defect_profiles'
AND column_name IN ('customer_id', 'product_id');
"
echo ""

echo "=== Migration Complete! ==="
echo ""
echo "Next step: Restart backend to apply changes"
echo "Run: docker compose -f docker-compose.prod.yml restart backend"
