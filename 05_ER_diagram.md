# Sentinel AI — Entity Relationship Diagram

Corresponds to `04_database_schema.sql`.

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ USERS : employs
    ORGANIZATIONS ||--o{ SITES : owns
    ROLES ||--o{ USERS : assigned_to
    ROLES ||--o{ ROLE_PERMISSIONS : has
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : granted_via
    USERS ||--o{ REFRESH_TOKENS : owns
    USERS ||--o{ AUDIT_LOGS : performs

    SITES ||--o{ ZONES : contains
    SITES ||--o{ CAMERAS : hosts
    ZONES ||--o{ CAMERAS : groups

    CAMERAS ||--o{ CAMERA_DETECTION_MODULES : configured_with
    CAMERAS ||--o{ INCIDENTS : detects
    CAMERAS ||--o{ AI_RESULTS : produces
    CAMERAS ||--o{ SUBJECT_MOVEMENTS : observes

    INCIDENT_TYPES ||--o{ INCIDENTS : classifies
    INCIDENT_TYPES ||--o{ NOTIFICATION_POLICIES : governs

    AI_MODEL_VERSIONS ||--o{ AI_RESULTS : generates

    INCIDENTS ||--o{ AI_RESULTS : supported_by
    INCIDENTS ||--o{ EVIDENCE : has
    INCIDENTS ||--o{ INCIDENT_REPORTS : documented_by
    INCIDENTS ||--o{ NOTIFICATIONS : triggers
    INCIDENTS ||--o{ TRACKED_SUBJECTS : involves
    INCIDENTS }o--|| USERS : confirmed_by

    TRACKED_SUBJECTS ||--o{ SUBJECT_MOVEMENTS : has_path

    SITES ||--o{ NOTIFICATION_POLICIES : defines

    ORGANIZATIONS ||--o{ SETTINGS : configures

    USERS {
        uuid id PK
        uuid organization_id FK
        string email
        string password_hash
        uuid role_id FK
        boolean is_active
    }

    CAMERAS {
        uuid id PK
        uuid site_id FK
        uuid zone_id FK
        string stream_type
        string status
    }

    INCIDENTS {
        uuid id PK
        string incident_type_code FK
        uuid camera_id FK
        uuid site_id FK
        string status
        numeric confidence_score
        string severity
        string priority
        timestamptz detected_at
    }

    AI_RESULTS {
        uuid id PK
        uuid incident_id FK
        uuid camera_id FK
        uuid model_version_id FK
        string result_type
        numeric confidence
    }

    EVIDENCE {
        uuid id PK
        uuid incident_id FK
        string evidence_type
        string storage_url
        string buffer_segment
        string checksum_sha256
    }

    NOTIFICATIONS {
        uuid id PK
        uuid incident_id FK
        string channel
        string status
    }
```

## Notes

- `incidents.status` state machine: `open → confirmed → escalated → resolved` or
  `open → dismissed/false_positive`.
- `evidence.checksum_sha256` supports chain-of-custody integrity verification.
- `camera_detection_modules` allows per-camera enable/disable of each AI model family
  without schema changes when new modules are added (module_code is a free-form string
  keyed against the AI service registry, not a hard FK — kept intentionally loose so new
  detection modules in Phase 3 don't require a migration).
