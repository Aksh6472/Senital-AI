-- ============================================================================
-- Sentinel AI — PostgreSQL Database Schema (Phase 1)
-- Normalized to 3NF. UUID primary keys. Soft-delete via deleted_at where relevant.
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";           -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "postgis";             -- for geography/location columns

-- ============================================================================
-- 1. IDENTITY & ACCESS
-- ============================================================================

CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(50) UNIQUE NOT NULL,      -- 'admin','operator','investigator','viewer','auditor'
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE permissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(100) UNIQUE NOT NULL,      -- 'incident:read','camera:write', etc.
    description     TEXT
);

CREATE TABLE role_permissions (
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    type            VARCHAR(50),                       -- 'residential','enterprise','municipal','hospital','campus'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    phone           VARCHAR(30),
    role_id         UUID NOT NULL REFERENCES roles(id),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    mfa_enabled     BOOLEAN NOT NULL DEFAULT false,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. SITES, ZONES & CAMERAS
-- ============================================================================

CREATE TABLE sites (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    address         TEXT,
    location        GEOGRAPHY(POINT, 4326),            -- lat/lon
    timezone        VARCHAR(64) NOT NULL DEFAULT 'UTC',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE zones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,              -- 'Lobby','Parking Lot B'
    description     TEXT
);

CREATE TABLE cameras (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id             UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    zone_id             UUID REFERENCES zones(id) ON DELETE SET NULL,
    name                VARCHAR(255) NOT NULL,
    stream_type         VARCHAR(20) NOT NULL,           -- 'rtsp','onvif','webcam','upload'
    stream_url          TEXT,
    location            GEOGRAPHY(POINT, 4326),
    status              VARCHAR(20) NOT NULL DEFAULT 'offline', -- 'online','offline','degraded'
    last_heartbeat_at   TIMESTAMPTZ,
    resolution          VARCHAR(20),
    fps                 SMALLINT,
    is_audio_enabled    BOOLEAN NOT NULL DEFAULT false,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE TABLE camera_detection_modules (
    camera_id       UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    module_code     VARCHAR(50) NOT NULL,               -- 'object_detection','pose','action','face', etc.
    is_enabled      BOOLEAN NOT NULL DEFAULT true,
    config          JSONB NOT NULL DEFAULT '{}',         -- thresholds, per-module overrides
    PRIMARY KEY (camera_id, module_code)
);

-- ============================================================================
-- 3. INCIDENT TAXONOMY
-- ============================================================================

CREATE TABLE incident_types (
    code            VARCHAR(50) PRIMARY KEY,             -- 'fire','theft','fall_detection', etc.
    category        VARCHAR(50) NOT NULL,                -- 'crime','traffic','fire_disaster','medical','public_safety'
    display_name    VARCHAR(100) NOT NULL,
    default_severity VARCHAR(20) NOT NULL,               -- 'low','medium','high','critical'
    default_response TEXT
);

-- ============================================================================
-- 4. AI RESULTS, INCIDENTS, EVIDENCE
-- ============================================================================

CREATE TABLE ai_model_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_family    VARCHAR(50) NOT NULL,                -- 'object_detection','pose', etc.
    model_name      VARCHAR(100) NOT NULL,               -- 'yolov11','mediapipe-pose'
    version         VARCHAR(50) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (model_family, model_name, version)
);

CREATE TABLE incidents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_type_code  VARCHAR(50) NOT NULL REFERENCES incident_types(code),
    camera_id           UUID NOT NULL REFERENCES cameras(id),
    site_id             UUID NOT NULL REFERENCES sites(id),
    status              VARCHAR(20) NOT NULL DEFAULT 'open', -- open,confirmed,escalated,resolved,dismissed,false_positive
    confidence_score    NUMERIC(5,2) NOT NULL,            -- 0.00 - 100.00
    severity            VARCHAR(20) NOT NULL,              -- low,medium,high,critical
    priority            VARCHAR(20) NOT NULL,              -- low,medium,high,urgent
    detected_objects    JSONB NOT NULL DEFAULT '[]',
    detected_actions     JSONB NOT NULL DEFAULT '[]',
    ai_explanation      TEXT,
    recommended_response TEXT,
    detected_at         TIMESTAMPTZ NOT NULL,
    confirmed_by        UUID REFERENCES users(id),
    confirmed_at        TIMESTAMPTZ,
    resolved_at         TIMESTAMPTZ,
    location            GEOGRAPHY(POINT, 4326),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_incidents_type ON incidents(incident_type_code);
CREATE INDEX idx_incidents_camera ON incidents(camera_id);
CREATE INDEX idx_incidents_detected_at ON incidents(detected_at DESC);
CREATE INDEX idx_incidents_status ON incidents(status);

CREATE TABLE ai_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id     UUID REFERENCES incidents(id) ON DELETE CASCADE,
    camera_id       UUID NOT NULL REFERENCES cameras(id),
    model_version_id UUID NOT NULL REFERENCES ai_model_versions(id),
    frame_timestamp TIMESTAMPTZ NOT NULL,
    result_type     VARCHAR(50) NOT NULL,                -- 'detection','pose','action','track','audio'
    payload         JSONB NOT NULL,                       -- bounding boxes, keypoints, class labels, scores
    confidence      NUMERIC(5,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ai_results_incident ON ai_results(incident_id);
CREATE INDEX idx_ai_results_camera_time ON ai_results(camera_id, frame_timestamp);

CREATE TABLE tracked_subjects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id     UUID REFERENCES incidents(id) ON DELETE CASCADE,
    subject_type    VARCHAR(20) NOT NULL,                 -- 'person','vehicle'
    attributes      JSONB NOT NULL DEFAULT '{}',           -- color, approx description, plate (if OCR'd)
    first_seen_at   TIMESTAMPTZ NOT NULL,
    last_seen_at    TIMESTAMPTZ NOT NULL
);

CREATE TABLE subject_movements (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracked_subject_id  UUID NOT NULL REFERENCES tracked_subjects(id) ON DELETE CASCADE,
    camera_id           UUID NOT NULL REFERENCES cameras(id),
    seen_at             TIMESTAMPTZ NOT NULL,
    bounding_box        JSONB NOT NULL,
    confidence          NUMERIC(5,2) NOT NULL
);

CREATE INDEX idx_subject_movements_subject ON subject_movements(tracked_subject_id, seen_at);

CREATE TABLE evidence (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id     UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    evidence_type   VARCHAR(20) NOT NULL,                 -- 'video_clip','image','audio'
    storage_url     TEXT NOT NULL,                         -- S3/MinIO object key
    buffer_segment  VARCHAR(20) NOT NULL,                  -- 'pre','during','post'
    duration_seconds INTEGER,
    checksum_sha256 VARCHAR(64) NOT NULL,                  -- chain-of-custody integrity
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_evidence_incident ON evidence(incident_id);

-- ============================================================================
-- 5. REPORTS
-- ============================================================================

CREATE TABLE incident_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id     UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    generated_by    UUID REFERENCES users(id),
    version         INTEGER NOT NULL DEFAULT 1,
    pdf_url         TEXT,
    operator_notes  TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 6. NOTIFICATIONS
-- ============================================================================

CREATE TABLE notification_policies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id             UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    incident_type_code  VARCHAR(50) NOT NULL REFERENCES incident_types(code),
    requires_confirmation BOOLEAN NOT NULL DEFAULT true,
    auto_escalate_threshold NUMERIC(5,2),                 -- confidence % above which auto-escalation is allowed
    recipients          JSONB NOT NULL DEFAULT '[]',        -- list of {type, contact_id/group}
    channels             JSONB NOT NULL DEFAULT '[]'         -- ['sms','email','push','whatsapp','voice','dashboard']
);

CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id     UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    channel         VARCHAR(20) NOT NULL,
    recipient       VARCHAR(255) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending,sent,delivered,failed
    sent_at         TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_incident ON notifications(incident_id);

-- ============================================================================
-- 7. AUDIT & SETTINGS
-- ============================================================================

CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,                 -- 'incident.confirm','camera.create', etc.
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       UUID,
    ip_address      INET,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);

CREATE TABLE settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    key             VARCHAR(100) NOT NULL,
    value           JSONB NOT NULL,
    updated_by      UUID REFERENCES users(id),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, key)
);

-- ============================================================================
-- 8. SEED DATA (incident taxonomy)
-- ============================================================================

INSERT INTO incident_types (code, category, display_name, default_severity, default_response) VALUES
('theft', 'crime', 'Theft', 'medium', 'Notify security personnel'),
('burglary', 'crime', 'Burglary', 'high', 'Notify police and homeowner'),
('robbery', 'crime', 'Robbery', 'critical', 'Dispatch police immediately'),
('armed_robbery', 'crime', 'Armed Robbery', 'critical', 'Dispatch police immediately, do not approach'),
('assault', 'crime', 'Assault', 'high', 'Dispatch police'),
('fighting', 'crime', 'Fighting', 'medium', 'Notify security personnel'),
('knife_attack', 'crime', 'Knife Attack', 'critical', 'Dispatch police and ambulance'),
('gun_threat', 'crime', 'Gun Threat', 'critical', 'Dispatch police immediately'),
('trespassing', 'crime', 'Trespassing', 'low', 'Notify security personnel'),
('vandalism', 'crime', 'Vandalism', 'low', 'Notify security personnel'),
('suspicious_loitering', 'crime', 'Suspicious Loitering', 'low', 'Notify security personnel'),
('vehicle_theft', 'crime', 'Vehicle Theft', 'medium', 'Notify police'),
('vehicle_collision', 'traffic', 'Vehicle Collision', 'high', 'Dispatch ambulance and police'),
('motorcycle_accident', 'traffic', 'Motorcycle Accident', 'high', 'Dispatch ambulance'),
('pedestrian_accident', 'traffic', 'Pedestrian Accident', 'critical', 'Dispatch ambulance immediately'),
('hit_and_run', 'traffic', 'Hit and Run', 'high', 'Notify police'),
('vehicle_fire', 'fire_disaster', 'Vehicle Fire', 'critical', 'Dispatch fire department'),
('overturned_vehicle', 'traffic', 'Overturned Vehicle', 'high', 'Dispatch ambulance and police'),
('fire', 'fire_disaster', 'Fire', 'critical', 'Dispatch fire department'),
('smoke', 'fire_disaster', 'Smoke', 'high', 'Investigate, prepare fire department dispatch'),
('explosion', 'fire_disaster', 'Explosion', 'critical', 'Dispatch fire, police, and ambulance'),
('person_collapse', 'medical', 'Person Collapse', 'critical', 'Dispatch ambulance'),
('fall_detection', 'medical', 'Fall Detection', 'high', 'Dispatch ambulance if unresponsive'),
('unconscious_person', 'medical', 'Unconscious Person', 'critical', 'Dispatch ambulance immediately'),
('crowd_panic', 'public_safety', 'Crowd Panic', 'high', 'Notify security and police'),
('stampede', 'public_safety', 'Stampede', 'critical', 'Dispatch police and ambulance'),
('restricted_area_entry', 'public_safety', 'Restricted Area Entry', 'medium', 'Notify security personnel'),
('abandoned_object', 'public_safety', 'Abandoned Object', 'medium', 'Notify security, monitor'),
('suspicious_package', 'public_safety', 'Suspicious Package', 'high', 'Notify security and police')
ON CONFLICT (code) DO NOTHING;
