# Sentinel AI — Software Requirements Specification (SRS)

**Version:** 1.0 · **Standard reference:** IEEE 830-style structure (adapted)

---

## 1. Introduction

### 1.1 Purpose
Defines functional and non-functional requirements for Sentinel AI v1, to guide backend,
AI pipeline, frontend, and DevOps implementation in Phases 2–5.

### 1.2 Scope
Covers camera ingestion, AI inference orchestration, incident lifecycle, evidence
management, notification, dashboard, GIS, and platform security/scalability. Excludes
model *training* infrastructure (v1 uses pretrained/fine-tuned models served via
inference services).

### 1.3 Definitions

| Term | Definition |
|---|---|
| Incident | A classified event produced by the AI Decision Engine with type, confidence, severity |
| Evidence Package | Video clip(s) + metadata + AI trace tied to one incident |
| Confidence Aggregation | Combining per-model confidence scores across frames/time into one incident confidence |
| Escalation | Notifying an external responder (police/fire/ambulance/security) |
| Camera Zone | Logical grouping of cameras (e.g., "Building A – Lobby") |

---

## 2. System Overview

Sentinel AI is a microservices platform with an async video ingestion layer, a modular AI
inference layer, a transactional core (incidents/evidence/users), a notification layer,
and a real-time web dashboard. See `03_ARCHITECTURE.md` for the full diagram.

---

## 3. Functional Requirements

### FR-1 Camera & Stream Management
- FR-1.1 System shall support adding RTSP, ONVIF/IP, webcam, and uploaded video sources.
- FR-1.2 System shall support simultaneous processing of 100+ camera streams (horizontally scalable).
- FR-1.3 System shall monitor per-camera health (online/offline/degraded/frame-drop rate).
- FR-1.4 System shall allow per-camera configuration of which detection modules are active.
- FR-1.5 System shall support camera grouping by site/zone/location with GPS coordinates.

### FR-2 AI Detection Pipeline
- FR-2.1 System shall run object detection on ingested frames (people, vehicles, weapons, fire/smoke, packages).
- FR-2.2 System shall run pose estimation for fall/collapse/seizure-like motion detection.
- FR-2.3 System shall run action/temporal-activity recognition across frame sequences (not single frames).
- FR-2.4 System shall run multi-object tracking to maintain identity across frames within a camera.
- FR-2.5 System shall support optional audio classification (gunshot, scream, glass break, explosion) where audio is available.
- FR-2.6 System shall aggregate multi-model, multi-frame confidence into a single incident confidence score before triggering an alert (no single-frame alerts).
- FR-2.7 AI pipeline shall be modular: each model runs as an independently deployable inference service behind a common interface, replaceable without changing the Decision Engine contract.

### FR-3 Incident Classification & Decision Engine
- FR-3.1 Every incident shall include: type, confidence score, threat level, severity, priority, detected objects, detected actions, recommended response, timestamp, camera ID, location.
- FR-3.2 Decision Engine shall apply configurable per-incident-type thresholds and multi-signal agreement rules before finalizing an incident.
- FR-3.3 System shall support a false-positive feedback loop: operator dismissals shall be logged and reportable per camera/incident-type.

### FR-4 Evidence Management
- FR-4.1 System shall automatically capture a configurable pre-incident buffer (default 30s), the full incident duration, and a post-incident buffer (default 30s).
- FR-4.2 Evidence shall be stored with bounding boxes, detected objects, confidence scores, model versions, and timestamps.
- FR-4.3 Evidence shall be searchable by incident type, camera, date/time range, and detected attributes (person/vehicle/weapon/color) where available.
- FR-4.4 Evidence storage shall be immutable/write-once for chain-of-custody; deletions require an auditable retention-policy action, not ad hoc deletion.

### FR-5 Incident Reporting
- FR-5.1 System shall auto-generate a structured incident report (ID, date/time, camera, location, type, summary, objects, actions, AI explanation, confidence, actions taken, evidence links, operator notes).
- FR-5.2 Reports shall be exportable as PDF.
- FR-5.3 Reports shall be versioned if operator notes are added after generation.

### FR-6 Notification & Escalation
- FR-6.1 System shall support SMS, email, push, WhatsApp, dashboard alert, and voice-call notification channels.
- FR-6.2 System shall support configurable recipient routing per incident type and per site (police/fire/ambulance/security/homeowner/building manager).
- FR-6.3 System shall support two workflow modes per incident type: (a) require human confirmation before external dispatch notification, (b) auto-escalate when confidence and multi-signal agreement exceed a configured high threshold.
- FR-6.4 All notifications shall be logged with delivery status.

### FR-7 Dashboard
- FR-7.1 Live camera grid with real-time AI overlay badges.
- FR-7.2 Incident feed with filter/search.
- FR-7.3 Threat timeline view.
- FR-7.4 Evidence viewer (video + bounding boxes + metadata).
- FR-7.5 Map view with camera and incident markers.
- FR-7.6 Analytics/statistics views (incidents by type/time/camera).
- FR-7.7 Notification center with delivery status.
- FR-7.8 Camera status and system health panel.
- FR-7.9 Dark mode, responsive layout.

### FR-8 GIS Integration
- FR-8.1 Map shall display camera locations, incident locations, and nearest police/fire/hospital facilities.
- FR-8.2 Map shall display estimated responder routes (via routing API integration).

### FR-9 Explainability
- FR-9.1 Every incident shall expose a plain-English explanation: which objects/actions were detected, how confidence was calculated, why the severity/threat classification was assigned.

### FR-10 Multi-Camera Tracking
- FR-10.1 System shall support re-identification of a tracked subject across multiple cameras within a site, subject to configuration and privacy policy.
- FR-10.2 System shall generate a movement/travel-path history for tracked subjects during an active incident investigation.

### FR-11 Search
- FR-11.1 System shall support search by person attributes, vehicle attributes, weapon type, color, camera, incident type, date/time, and location.

### FR-12 Users, Roles & Permissions
- FR-12.1 System shall support RBAC with at least: Admin, Operator, Investigator, Viewer, Auditor roles.
- FR-12.2 All privileged actions shall be permission-checked server-side, not just hidden in UI.

---

## 4. Non-Functional Requirements

### NFR-1 Performance
- Detection-to-alert latency < 3s p95 per FR pipeline stage budget.
- Dashboard live feed latency < 2s glass-to-glass (WebRTC) target.

### NFR-2 Scalability
- Horizontally scalable inference workers; stateless API services behind a load balancer.
- Kafka (or equivalent) for event/frame-metadata streaming between ingestion and inference.
- Redis for caching/session/pub-sub of live alerts.

### NFR-3 Security
- JWT-based authentication, RBAC authorization, TLS/HTTPS everywhere.
- Encryption at rest for evidence storage and PII.
- Rate limiting and input validation on all public APIs.
- Full audit logging of privileged actions (who/what/when).

### NFR-4 Reliability & Availability
- Target 99.9% uptime; graceful degradation if an AI service is unavailable (fall back to recording-only with alert to admins).

### NFR-5 Maintainability
- Modular AI interfaces (swap models without changing Decision Engine contract).
- Clean Architecture / DDD boundaries between domain, application, and infrastructure layers.
- OpenAPI-documented, versioned REST APIs.

### NFR-6 Privacy & Compliance
- Configurable data retention per jurisdiction.
- Face recognition module disabled by default, separately access-controlled and audited when enabled.
- Data subject access / deletion workflows for jurisdictions requiring them (GDPR-style).

### NFR-7 Observability
- Structured logging, distributed tracing across microservices, metrics (Prometheus-style) for inference latency, queue depth, false-positive rate.

---

## 5. External Interface Requirements

- **Camera interfaces:** RTSP, ONVIF, HTTP file upload, WebRTC ingestion for browser-based cameras.
- **Notification providers:** SMS/voice (e.g., Twilio-class), email (SMTP/SendGrid-class), push (FCM/APNs-class), WhatsApp Business API.
- **Mapping/GIS:** Mapbox/Google Maps/OpenStreetMap-class provider for map rendering and routing.
- **Object storage:** S3-compatible (AWS S3 or MinIO) for evidence.

---

## 6. Data Requirements

See `04_database_schema.sql` and `05_ER_diagram.md` for the full normalized schema
covering users, roles, permissions, cameras, incidents, alerts, evidence, AI results,
reports, audit logs, notification history, and settings.

---

## 7. Traceability

Each functional requirement (FR-x.x) maps to a service defined in
`03_ARCHITECTURE.md` §4 (Service Boundaries) and will be traced to specific modules in
Phases 2–4 deliverables.
