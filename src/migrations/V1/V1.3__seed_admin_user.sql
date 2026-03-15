-- Seed a default admin user for development and testing.
-- Email: test@admin.com | Password: Cloud.456
-- Password hash is sha256_crypt (passlib), compatible with JWT_ALGORITHM=HS256.
INSERT INTO public.user (id, username, email, password, is_admin, disabled, oidc_configs)
SELECT uuid_generate_v4(), 'admin', 'test@admin.com',
    '$5$rounds=535000$8ws.bvUTex83mhMg$ujSsZgI7F7OrtqVVYynHGH3d23SMuncuUIa4.aJ6kQD',
    true, false, '[]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM public.user WHERE email = 'test@admin.com');
