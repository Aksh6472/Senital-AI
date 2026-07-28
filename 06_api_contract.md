# Sentinel AI — API Contract Outline (v1)

Base path: `/api/v1`. All endpoints require `Authorization: Bearer <JWT>` except
`/auth/login` and `/auth/refresh`. Full OpenAPI spec will be generated from the FastAPI
implementation in Phase 2 — this is the design-time contract.

## Auth
| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Email/password → access + refresh token |
| POST | `/auth/refresh` | Refresh token → new access token |
| POST | `/auth/logout` | Revoke refresh token |
| GET | `/auth/me` | Current user profile + permissions |

## Cameras
| Method | Path | Description |
|---|---|---|
| GET | `/cameras` | List cameras (filter by site/zone/status) |
| POST | `/cameras` | Register new camera |
| GET | `/cameras/{id}` | Camera detail |
| PATCH | `/cameras/{id}` | Update camera config |
| DELETE | `/cameras/{id}` | Soft-delete camera |
| GET | `/cameras/{id}/health` | Live health/status |
| PUT | `/cameras/{id}/detection-modules` | Configure active AI modules |

## Incidents
| Method | Path | Description |
|---|---|---|
| GET | `/incidents` | List/search incidents (type, camera, date range, status) |
| GET | `/incidents/{id}` | Incident detail incl. AI explanation |
| POST | `/incidents/{id}/confirm` | Operator confirms incident |
| POST | `/incidents/{id}/dismiss` | Operator dismisses (false positive) |
| POST | `/incidents/{id}/escalate` | Manually trigger escalation |
| GET | `/incidents/{id}/timeline` | Full event/state timeline |

## Evidence
| Method | Path | Description |
|---|---|---|
| GET | `/incidents/{id}/evidence` | List evidence items for an incident |
| GET | `/evidence/{id}` | Signed URL / metadata for one item |
| GET | `/evidence/search` | Search by attributes (person/vehicle/color/etc.) |

## Reports
| Method | Path | Description |
|---|---|---|
| POST | `/incidents/{id}/report` | Generate report (returns report id) |
| GET | `/reports/{id}` | Report metadata |
| GET | `/reports/{id}/pdf` | Download PDF |

## Notifications
| Method | Path | Description |
|---|---|---|
| GET | `/notification-policies` | List policies per site/incident type |
| PUT | `/notification-policies/{id}` | Update routing/threshold config |
| GET | `/incidents/{id}/notifications` | Delivery status for an incident |

## Analytics
| Method | Path | Description |
|---|---|---|
| GET | `/analytics/summary` | Incident counts by type/severity/time |
| GET | `/analytics/camera/{id}` | Per-camera stats incl. false-positive rate |

## GIS
| Method | Path | Description |
|---|---|---|
| GET | `/gis/cameras` | GeoJSON of camera locations |
| GET | `/gis/incidents` | GeoJSON of recent incident locations |
| GET | `/gis/nearest-responders` | Nearest police/fire/hospital for a location |

## Admin
| Method | Path | Description |
|---|---|---|
| GET/POST | `/users` | User management |
| GET/POST | `/roles` | Role/permission management |
| GET | `/audit-logs` | Searchable audit trail |
| GET/PUT | `/settings` | Org-level settings |

## Real-time channels (WebSocket / SSE)
| Channel | Payload |
|---|---|
| `ws://.../live/incidents` | New/updated incidents (pub/sub via Redis) |
| `ws://.../live/camera/{id}` | Live health + AI overlay events for one camera |

## Conventions
- Pagination: `?page=&page_size=` with `X-Total-Count` header.
- Errors: RFC 7807-style problem+json (`type`, `title`, `status`, `detail`, `instance`).
- Versioning: URI-based (`/api/v1`), additive changes preferred over breaking changes.
- All list endpoints support field-based filtering and `sort=field:asc|desc`.
