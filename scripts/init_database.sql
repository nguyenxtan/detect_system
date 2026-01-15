-- Defect Recognition System Database Schema
-- PostgreSQL + pgvector

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'qc', 'user')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on username and email
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Defect Profiles Table (Knowledge Base)
CREATE TABLE IF NOT EXISTS defect_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer VARCHAR(100) NOT NULL,
    part_code VARCHAR(50) NOT NULL,
    part_name VARCHAR(100) NOT NULL,
    defect_type VARCHAR(50) NOT NULL CHECK (defect_type IN ('can', 'rach', 'nhan', 'phong', 'ok')),
    defect_title VARCHAR(200) NOT NULL,
    defect_description TEXT NOT NULL,
    keywords TEXT[],
    severity VARCHAR(20) DEFAULT 'minor' CHECK (severity IN ('minor', 'major', 'critical')),
    reference_images TEXT[],
    image_embedding vector(512),
    text_embedding vector(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on defect_profiles
CREATE INDEX idx_defect_profiles_customer ON defect_profiles(customer);
CREATE INDEX idx_defect_profiles_part_code ON defect_profiles(part_code);
CREATE INDEX idx_defect_profiles_defect_type ON defect_profiles(defect_type);

-- Create vector indexes for similarity search
CREATE INDEX idx_defect_profiles_image_embedding ON defect_profiles
USING ivfflat (image_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_defect_profiles_text_embedding ON defect_profiles
USING ivfflat (text_embedding vector_cosine_ops) WITH (lists = 100);

-- Defect Incidents Table (User submissions)
CREATE TABLE IF NOT EXISTS defect_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) NOT NULL,
    defect_profile_id UUID REFERENCES defect_profiles(id),
    predicted_defect_type VARCHAR(50),
    confidence FLOAT,
    image_url VARCHAR(500) NOT NULL,
    image_embedding vector(512),
    model_version VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on defect_incidents
CREATE INDEX idx_defect_incidents_user_id ON defect_incidents(user_id);
CREATE INDEX idx_defect_incidents_created_at ON defect_incidents(created_at DESC);
CREATE INDEX idx_defect_incidents_defect_profile_id ON defect_incidents(defect_profile_id);

-- Insert default admin user (password: admin123)
-- Password hash generated with bcrypt 3.2.0
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$0KbsdOlPLi9JfViUPLLTL.j22ViP7.yXiNO5wf4pB/V6t98BOSsoa',
    'Administrator',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Insert demo QC user (password: qc123)
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES (
    'qc_user',
    'qc@example.com',
    '$2b$12$8rVWmQqFoH5WqPr5HYxLeeX8L7vN.xYYYH8Y8YqL8Z8F8Z8F8Z8F8',
    'QC Inspector',
    'qc'
) ON CONFLICT (username) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_defect_profiles_updated_at BEFORE UPDATE ON defect_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample defect profile data (for testing)
-- Uncomment to insert sample data

/*
INSERT INTO defect_profiles (
    customer, part_code, part_name, defect_type, defect_title,
    defect_description, keywords, severity
) VALUES (
    'FAPV',
    'GD3346',
    'Grommet',
    'can',
    'Cấn',
    'Trên bề mặt sản phẩm xuất hiện vết lõm kéo dài, có thể do bị ép, va đập hoặc gấp trong quá trình sản xuất hoặc vận chuyển.',
    ARRAY['can', 'vet lom', 'ep', 'gap', 'va dap'],
    'major'
);

INSERT INTO defect_profiles (
    customer, part_code, part_name, defect_type, defect_title,
    defect_description, keywords, severity
) VALUES (
    'FAPV',
    'GD3346',
    'Grommet',
    'rach',
    'Rách',
    'Sản phẩm bị rách, có vết cắt hoặc đứt gãy ở bề mặt, ảnh hưởng đến tính toàn vẹn của sản phẩm.',
    ARRAY['rach', 'cut', 'tear', 'duc', 'cat'],
    'critical'
);
*/

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
