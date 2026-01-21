-- Migration: Add customer_id and product_id to defect_profiles table
-- Date: 2026-01-21
-- Purpose: Support context-based filtering for defect matching

-- Add customer_id column
ALTER TABLE defect_profiles
ADD COLUMN IF NOT EXISTS customer_id INTEGER;

-- Add product_id column
ALTER TABLE defect_profiles
ADD COLUMN IF NOT EXISTS product_id INTEGER;

-- Add foreign key constraint for customer_id
ALTER TABLE defect_profiles
ADD CONSTRAINT fk_defect_profile_customer
FOREIGN KEY (customer_id)
REFERENCES customers(id)
ON DELETE RESTRICT;

-- Add foreign key constraint for product_id
ALTER TABLE defect_profiles
ADD CONSTRAINT fk_defect_profile_product
FOREIGN KEY (product_id)
REFERENCES products(id)
ON DELETE RESTRICT;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_defect_profiles_customer_id ON defect_profiles(customer_id);
CREATE INDEX IF NOT EXISTS idx_defect_profiles_product_id ON defect_profiles(product_id);

-- Verify columns were added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'defect_profiles'
AND column_name IN ('customer_id', 'product_id');
