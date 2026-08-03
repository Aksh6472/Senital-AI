-- ============================================================================
-- Sentinel AI — Seed Data (Identity, Access & Defaults)
-- ============================================================================

-- 1. Organizations & Sites
INSERT INTO organizations (id, name, type) VALUES
('00000000-0000-0000-0000-000000000001', 'Sentinel AI Headquarters', 'enterprise')
ON CONFLICT (id) DO NOTHING;

INSERT INTO sites (id, organization_id, name, address, timezone) VALUES
('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Main Campus', '123 Security Way, Tech City', 'UTC')
ON CONFLICT (id) DO NOTHING;

INSERT INTO zones (id, site_id, name, description) VALUES
('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000002', 'Main Lobby', 'Front entrance lobby')
ON CONFLICT (id) DO NOTHING;

-- 2. Roles
INSERT INTO roles (id, name, description) VALUES
('10000000-0000-0000-0000-000000000001', 'admin', 'System Administrator with full access'),
('10000000-0000-0000-0000-000000000002', 'operator', 'Control room operator, handles incidents and cameras'),
('10000000-0000-0000-0000-000000000003', 'investigator', 'Reviews past incidents and evidence'),
('10000000-0000-0000-0000-000000000004', 'viewer', 'Read-only viewer'),
('10000000-0000-0000-0000-000000000005', 'auditor', 'Audit log viewer')
ON CONFLICT (id) DO NOTHING;

-- 3. Permissions
INSERT INTO permissions (id, code, description) VALUES
('20000000-0000-0000-0000-000000000001', 'user:create', 'Create new users'),
('20000000-0000-0000-0000-000000000002', 'user:read', 'Read user profiles'),
('20000000-0000-0000-0000-000000000003', 'user:write', 'Update user profiles'),
('20000000-0000-0000-0000-000000000004', 'user:delete', 'Soft-delete users'),
('20000000-0000-0000-0000-000000000005', 'role:read', 'Read system roles'),
('20000000-0000-0000-0000-000000000006', 'role:write', 'Modify role permissions'),
('20000000-0000-0000-0000-000000000007', 'camera:create', 'Register new cameras'),
('20000000-0000-0000-0000-000000000008', 'camera:read', 'View cameras and health'),
('20000000-0000-0000-0000-000000000009', 'camera:write', 'Update cameras and configure AI modules'),
('20000000-0000-0000-0000-000000000010', 'camera:delete', 'De-register cameras'),
('20000000-0000-0000-0000-000000000011', 'incident:create', 'Manually report incidents or receive from AI'),
('20000000-0000-0000-0000-000000000012', 'incident:read', 'View incident lifecycle and details'),
('20000000-0000-0000-0000-000000000013', 'incident:write', 'Update, escalate, resolve incidents'),
('20000000-0000-0000-0000-000000000014', 'incident:delete', 'Delete incidents'),
('20000000-0000-0000-0000-000000000015', 'policy:read', 'View notification policies'),
('20000000-0000-0000-0000-000000000016', 'policy:write', 'Update notification policies'),
('20000000-0000-0000-0000-000000000017', 'audit:read', 'View audit log history')
ON CONFLICT (id) DO NOTHING;

-- 4. Role Permissions Mapping
-- Admin gets all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT '10000000-0000-0000-0000-000000000001', id FROM permissions
ON CONFLICT DO NOTHING;

-- Operator permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT '10000000-0000-0000-0000-000000000002', id FROM permissions 
WHERE code IN ('camera:read', 'camera:write', 'incident:create', 'incident:read', 'incident:write', 'policy:read', 'policy:write')
ON CONFLICT DO NOTHING;

-- Investigator permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT '10000000-0000-0000-0000-000000000003', id FROM permissions 
WHERE code IN ('camera:read', 'incident:read', 'incident:write')
ON CONFLICT DO NOTHING;

-- Viewer permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT '10000000-0000-0000-0000-000000000004', id FROM permissions 
WHERE code IN ('camera:read', 'incident:read')
ON CONFLICT DO NOTHING;

-- Auditor permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT '10000000-0000-0000-0000-000000000005', id FROM permissions 
WHERE code IN ('audit:read', 'user:read')
ON CONFLICT DO NOTHING;

-- 5. Default Users
-- admin@sentinel.ai / adminpassword
INSERT INTO users (id, organization_id, email, password_hash, full_name, role_id, is_active) VALUES
('30000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'admin@sentinel.ai', crypt('adminpassword', gen_salt('bf', 12)), 'System Admin', '10000000-0000-0000-0000-000000000001', true)
ON CONFLICT (id) DO NOTHING;

-- operator@sentinel.ai / operatorpassword
INSERT INTO users (id, organization_id, email, password_hash, full_name, role_id, is_active) VALUES
('30000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'operator@sentinel.ai', crypt('operatorpassword', gen_salt('bf', 12)), 'Control Room Operator', '10000000-0000-0000-0000-000000000002', true)
ON CONFLICT (id) DO NOTHING;

-- 6. Default Cameras
INSERT INTO cameras (id, site_id, zone_id, name, stream_type, stream_url, status, resolution, fps, is_audio_enabled) VALUES
('40000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000003', 'Lobby Camera 1', 'rtsp', 'rtsp://192.168.1.50:554/stream1', 'online', '1080p', 30, true)
ON CONFLICT (id) DO NOTHING;

-- Enable AI modules for the camera
INSERT INTO camera_detection_modules (camera_id, module_code, is_enabled, config) VALUES
('40000000-0000-0000-0000-000000000001', 'object_detection', true, '{"confidence_threshold": 0.5}'),
('40000000-0000-0000-0000-000000000001', 'action_recognition', true, '{"confidence_threshold": 0.6}'),
('40000000-0000-0000-0000-000000000001', 'tracking', true, '{"iou_threshold": 0.3}')
ON CONFLICT (camera_id, module_code) DO NOTHING;

-- 7. Seed Notification Policies for the Site
INSERT INTO notification_policies (id, site_id, incident_type_code, requires_confirmation, auto_escalate_threshold, recipients, channels) VALUES
('50000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'fire', false, 85.00, '[{"type": "email", "address": "fire-alerts@sentinel-ai.local"}]', '["email", "dashboard"]'),
('50000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002', 'gun_threat', false, 90.00, '[{"type": "sms", "phone": "+15550199"}]', '["sms", "dashboard"]')
ON CONFLICT (id) DO NOTHING;
