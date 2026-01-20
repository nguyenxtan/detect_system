-- Context-based filtering: Add foreign keys to defect_profiles table
-- This migration is BACKWARD COMPATIBLE (all new fields are nullable)

-- Migration: 002_add_context_foreign_keys
-- Date: 2026-01-20
-- Description: Add customer_id and product_id foreign keys to defect_profiles for QC-standard context filtering

BEGIN;

-- Add foreign key columns to defect_profiles table
ALTER TABLE defect_profiles
    ADD COLUMN IF NOT EXISTS customer_id INTEGER,
    ADD COLUMN IF NOT EXISTS product_id INTEGER;

-- Add foreign key constraints (using DO block for idempotency)
DO $$
BEGIN
    -- Add customer foreign key if not exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_defect_profiles_customer'
    ) THEN
        ALTER TABLE defect_profiles
            ADD CONSTRAINT fk_defect_profiles_customer
                FOREIGN KEY (customer_id)
                REFERENCES customers(id)
                ON DELETE RESTRICT;
    END IF;

    -- Add product foreign key if not exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_defect_profiles_product'
    ) THEN
        ALTER TABLE defect_profiles
            ADD CONSTRAINT fk_defect_profiles_product
                FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE RESTRICT;
    END IF;
END $$;

-- Add indexes for efficient filtering
CREATE INDEX IF NOT EXISTS idx_defect_profiles_customer_id
    ON defect_profiles(customer_id);

CREATE INDEX IF NOT EXISTS idx_defect_profiles_product_id
    ON defect_profiles(product_id);

-- Composite index for context-based queries (customer + product filtering)
CREATE INDEX IF NOT EXISTS idx_defect_profiles_context
    ON defect_profiles(customer_id, product_id)
    WHERE customer_id IS NOT NULL AND product_id IS NOT NULL;

-- Add comments for documentation
COMMENT ON COLUMN defect_profiles.customer_id IS 'Foreign key to customers table for context-based filtering';
COMMENT ON COLUMN defect_profiles.product_id IS 'Foreign key to products table for context-based filtering';

COMMIT;

-- Rollback script (if needed):
-- BEGIN;
-- ALTER TABLE defect_profiles
--     DROP CONSTRAINT IF EXISTS fk_defect_profiles_product,
--     DROP CONSTRAINT IF EXISTS fk_defect_profiles_customer,
--     DROP COLUMN IF EXISTS product_id,
--     DROP COLUMN IF EXISTS customer_id;
-- COMMIT;
