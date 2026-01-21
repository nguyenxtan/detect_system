-- Migration 003: Add OK defect type and NONE severity level
-- This allows users to create reference profiles for defect-free (normal) images

-- Insert NONE severity level if not exists
INSERT INTO severity_levels (severity_code, name_vi, name_en, created_at)
SELECT 'NONE', 'Không có lỗi', 'No Defect', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM severity_levels WHERE severity_code = 'NONE'
);

-- Insert OK defect type if not exists
INSERT INTO defect_types (defect_code, name_vi, name_en, created_at)
SELECT 'OK', 'Không có lỗi (Bình thường)', 'OK / No Defect (Normal)', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM defect_types WHERE defect_code = 'OK'
);
