-- Phase 3: Add vision pipeline fields to defect_incidents table
-- This migration is BACKWARD COMPATIBLE (all new fields are nullable)

-- Migration: 001_add_vision_fields
-- Date: 2026-01-18
-- Description: Add vision pipeline fields for two-stage detection

BEGIN;

-- Add vision pipeline fields to defect_incidents table
ALTER TABLE defect_incidents
    ADD COLUMN IF NOT EXISTS vision_enabled BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS vision_result VARCHAR(10),  -- "OK" or "NG"
    ADD COLUMN IF NOT EXISTS anomaly_score FLOAT,
    ADD COLUMN IF NOT EXISTS defect_regions JSONB,  -- Array of detected regions
    ADD COLUMN IF NOT EXISTS vision_model_version VARCHAR(100),
    ADD COLUMN IF NOT EXISTS detectors_used TEXT[],  -- Array of detector names
    ADD COLUMN IF NOT EXISTS processing_time_ms FLOAT,
    ADD COLUMN IF NOT EXISTS vision_processing_time_ms FLOAT,
    ADD COLUMN IF NOT EXISTS clip_processing_time_ms FLOAT;

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_defect_incidents_vision_result
    ON defect_incidents(vision_result)
    WHERE vision_enabled = TRUE;

CREATE INDEX IF NOT EXISTS idx_defect_incidents_anomaly_score
    ON defect_incidents(anomaly_score)
    WHERE vision_enabled = TRUE;

-- Add comment for documentation
COMMENT ON COLUMN defect_incidents.vision_enabled IS 'Whether vision pipeline was used for this incident';
COMMENT ON COLUMN defect_incidents.vision_result IS 'OK or NG from VisionEngine';
COMMENT ON COLUMN defect_incidents.anomaly_score IS 'Anomaly score from 0.0 (normal) to 1.0 (anomalous)';
COMMENT ON COLUMN defect_incidents.defect_regions IS 'JSON array of detected defect regions: [{x, y, w, h, defect_type, confidence, detector_name}]';
COMMENT ON COLUMN defect_incidents.vision_model_version IS 'Version of vision engine used';
COMMENT ON COLUMN defect_incidents.detectors_used IS 'Array of detector names that found defects';

COMMIT;

-- Rollback script (if needed):
-- BEGIN;
-- ALTER TABLE defect_incidents
--     DROP COLUMN IF EXISTS vision_enabled,
--     DROP COLUMN IF EXISTS vision_result,
--     DROP COLUMN IF EXISTS anomaly_score,
--     DROP COLUMN IF EXISTS defect_regions,
--     DROP COLUMN IF EXISTS vision_model_version,
--     DROP COLUMN IF EXISTS detectors_used,
--     DROP COLUMN IF EXISTS processing_time_ms,
--     DROP COLUMN IF EXISTS vision_processing_time_ms,
--     DROP COLUMN IF EXISTS clip_processing_time_ms;
-- COMMIT;
