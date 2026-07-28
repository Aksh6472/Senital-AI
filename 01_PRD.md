# Sentinel AI — Product Requirements Document (PRD)

**Version:** 1.0
**Status:** Draft — Phase 1 (Foundation)
**Owner:** Product / Engineering

---

## 1. Executive Summary

Sentinel AI is an AI-powered emergency detection and response platform that converts
existing CCTV, IP cameras, doorbell cameras, and RTSP streams into an intelligent
monitoring network. Instead of passively recording footage for later review, Sentinel AI
continuously analyzes live video (and optionally audio) using a multi-stage AI pipeline to
detect crimes, accidents, fires, medical emergencies, and public-safety incidents in real
time, then classifies severity, preserves evidence, and notifies the correct responders
through a configurable workflow.

## 2. Problem Statement

Traditional surveillance is reactive: footage is reviewed after an incident, or a human
operator must watch dozens of feeds simultaneously. This leads to delayed response,
missed incidents, operator fatigue, and preventable harm — especially when a victim is
incapacitated and cannot call for help themselves. Sentinel AI's goal is to close that gap
by acting as an always-on analytical layer over existing camera infrastructure.

## 3. Goals & Non-Goals

**Goals**
- Real-time, multi-signal incident detection with low false-positive rates.
- Human-in-the-loop escalation workflow — AI assists, humans confirm dispatch by default.
- Full evidence chain (pre/during/post clips, metadata, AI reasoning) for every incident.
- Auditable, explainable AI decisions suitable for legal/operational review.
- Modular AI layer so individual models can be swapped/upgraded independently.
- Enterprise-grade security, RBAC, and data governance from day one.

**Non-Goals (explicitly out of scope for v1)**
- Fully autonomous dispatch without any human confirmation path (see §9, Safety).
- Real-time facial-recognition identity matching against external watchlists — this
  requires separate legal/compliance review per deployment jurisdiction and is treated as
  an optional, disabled-by-default module, not a core feature.
- Training bespoke action-recognition models from scratch — v1 uses pretrained/fine-tunable
  open models; a dedicated data-collection/labeling effort is a future phase.

## 4. Target Users / Personas

| Persona | Needs |
|---|---|
| **Security Operator** | Live dashboard, fast triage, one-click escalate/dismiss |
| **Facility/Building Manager** | Incident history, reports, camera health, cost oversight |
| **Law Enforcement Liaison** | Verified evidence packages, chain-of-custody, GIS context |
| **System Administrator** | Camera onboarding, user/role management, system health |
| **Compliance/Legal** | Audit logs, data retention controls, access reviews |

## 5. Core User Journeys

1. **Camera onboarding** — Admin registers an RTSP/IP camera, assigns it to a zone/location,
   configures which detection modules are active for that camera.
2. **Live monitoring** — Operator views the live grid; an AI badge appears on a feed the
   moment a candidate event crosses a confidence threshold, with a live explanation panel.
3. **Incident escalation** — When multi-signal confidence is high, the system either
   auto-escalates (per configurable policy) or prompts the operator to confirm within an
   SLA window before notifying external responders.
4. **Evidence review** — Investigator searches by incident type/date/camera/person/vehicle
   attributes, opens the evidence package (clip + bounding boxes + AI trace), and exports a
   signed PDF incident report.
5. **Post-incident audit** — Compliance reviews the full decision trail: which models fired,
   confidence scores, who confirmed/dismissed, and notification history.

## 6. Functional Requirements Summary

See the companion **Software Requirements Specification (02_SRS.md)** for the full,
numbered functional/non-functional requirements. At a high level v1 must support:

- Multi-camera ingestion (RTSP, ONVIF/IP, file upload, webcam)
- Multi-stage AI pipeline (detection → tracking → action recognition → temporal
  aggregation → decision engine)
- Incident classification (type, confidence, severity, priority, recommended response)
- Evidence capture with configurable pre/post buffers
- Configurable notification routing (SMS, email, push, WhatsApp, dashboard, voice)
- Live dashboard (grid, incident feed, map, analytics, notification center)
- GIS overlay (cameras, incidents, nearest responders, routes)
- Explainability panel per incident
- Cross-camera tracking within a single site (multi-camera re-identification)
- RBAC, audit logging, encrypted storage

## 7. Success Metrics

| Metric | Target (v1) |
|---|---|
| False positive rate (auto-escalated incidents) | < 5% |
| Detection-to-alert latency | < 3 seconds (p95) |
| Operator confirmation SLA | < 30 seconds median |
| Evidence retrieval time | < 2 seconds for indexed search |
| System uptime | 99.9% (excluding scheduled maintenance) |
| Camera capacity (v1 target) | 100+ concurrent streams per cluster |

## 8. Assumptions & Constraints

- Deployments are on-prem, hybrid, or cloud (AWS/GCP/Azure) with GPU-capable inference
  nodes; edge-only deployments are a future consideration.
- Camera infrastructure supports standard RTSP/ONVIF; proprietary protocols require
  adapters (future work).
- Legal responsibility for actually dispatching emergency services rests with the human
  operator/organization, not the AI, in the default configuration.

## 9. Safety, Ethics & Compliance Notes

- **Human confirmation by default.** Auto-escalation without human confirmation is an
  opt-in configuration per incident *type*, not a global default, and should be limited to
  the highest-confidence, highest-severity categories (e.g., fire) where deployers
  explicitly accept that tradeoff.
- **Data minimization & retention.** Evidence retention periods must be configurable per
  jurisdiction; PII (faces, plates) should be access-controlled separately from general
  operational data.
- **Face recognition is opt-in and jurisdiction-gated**, disabled by default, and logged
  distinctly from other detections given its regulatory sensitivity (BIPA, GDPR, etc.).
- **Bias & false positives.** Action-recognition and pose-based models must be validated
  across demographics before production use; the platform must log and surface
  false-positive/override rates per camera and per incident type so operators can
  recalibrate thresholds.
- This PRD assumes the deploying organization has legal authority to operate surveillance
  at each installed site and has completed any required privacy/DPIA review; the platform
  provides the controls (consent flags, retention policy, audit trail) but does not itself
  grant legal authority.

## 10. Deliverables Roadmap

| Phase | Contents |
|---|---|
| 1 — Foundation (this phase) | PRD, SRS, architecture, DB schema, folder structure, API contract |
| 2 | Backend core services (auth, camera mgmt, incidents, notifications) |
| 3 | AI detection pipeline (modular inference services) |
| 4 | Frontend dashboard (Next.js) |
| 5 | DevOps (Docker/K8s, CI/CD, deployment guide, production checklist) |

## 11. Open Questions

- Which jurisdictions/deployment types are v1 targeting first (residential vs. enterprise
  vs. municipal)? This affects default retention and face-recognition policy.
- Preferred cloud vs. on-prem GPU strategy for the initial pilot.
- Which external notification providers (Twilio, SendGrid, WhatsApp Business API, etc.)
  should be wired first.
