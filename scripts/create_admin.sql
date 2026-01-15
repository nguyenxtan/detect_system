-- Create admin user
-- Password: admin123
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lW8hQXlXmSFW',
    'Administrator',
    'admin'
) ON CONFLICT (username) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password,
    role = EXCLUDED.role;

-- Verify
SELECT id, username, email, role, is_active FROM users WHERE username = 'admin';
