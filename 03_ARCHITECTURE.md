# Sentinel AI — System Architecture

## 1. Architectural Style

Microservices, event-driven where it matters (ingestion → inference → decision → notify),
synchronous REST where it's simpler (CRUD, dashboard queries). Clean Architecture / DDD
layering inside each service: `domain` → `application` → `infrastructure` → `api`.

## 2. High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph Sources["Video / Audio Sources"]
        CCTV[CCTV / IP Cameras]
        Doorbell[Smart Doorbells]
        RTSP[RTSP Streams]
        Upload[Uploaded Video]
    end

    subgraph Ingestion["Ingestion Layer"]
        StreamGW[Stream Gateway<br/>RTSP/ONVIF/WebRTC]
        FrameSampler[Frame Sampler & Preprocessor]
    end

    subgraph Bus["Event Bus"]
        Kafka[(Kafka: frame-events,<br/>ai-results, incidents)]
        Redis[(Redis: cache, pub/sub,<br/>live alert fanout)]
    end

    subgraph AI["Modular AI Inference Layer"]
        ObjDet[Object Detection<br/>YOLOv11 / RT-DETR]
        Pose[Pose Estimation<br/>MediaPipe/OpenPose]
        Action[Action Recognition<br/>SlowFast/VideoSwin/TimeSformer]
        Track[Tracking<br/>ByteTrack/DeepSORT]
        Seg[Segmentation<br/>SAM2]
        Face[Face Recognition<br/>FaceNet — opt-in]
        OCR[OCR<br/>EasyOCR]
        Audio[Audio Classification<br/>gunshot/scream/glass]
        Whisper[Speech-to-Text<br/>Whisper — optional]
    end

    subgraph Decision["Decision & Core Services"]
        Aggregator[Confidence Aggregation<br/>+ Temporal Analysis]
        DecisionEngine[AI Decision Engine]
        IncidentSvc[Incident Service]
        EvidenceSvc[Evidence Service]
        ReportSvc[Reporting Service]
    end

    subgraph Platform["Platform Services"]
        Auth[Auth Service<br/>JWT/RBAC]
        CameraSvc[Camera Mgmt Service]
        NotifySvc[Notification Service]
        AnalyticsSvc[Analytics Service]
        GISSvc[GIS Service]
        AuditSvc[Audit Logging Service]
    end

    subgraph Storage["Storage"]
        Postgres[(PostgreSQL)]
        S3[(S3 / MinIO<br/>Evidence Store)]
    end

    subgraph Clients["Clients"]
        Dashboard[Next.js Dashboard]
        MobilePush[Mobile / Push]
    end

    subgraph External["External Responders"]
        Police[Police]
        Fire[Fire Dept]
        Ambulance[Ambulance]
        Security[Security Personnel]
    end

    CCTV --> StreamGW
    Doorbell --> StreamGW
    RTSP --> StreamGW
    Upload --> StreamGW
    StreamGW --> FrameSampler --> Kafka

    Kafka --> ObjDet & Pose & Action & Track & Seg & Face & OCR & Audio & Whisper
    ObjDet & Pose & Action & Track & Seg & Face & OCR & Audio & Whisper --> Aggregator
    Aggregator --> DecisionEngine --> IncidentSvc
    IncidentSvc --> EvidenceSvc --> S3
    IncidentSvc --> ReportSvc
    IncidentSvc --> NotifySvc --> Police & Fire & Ambulance & Security
    IncidentSvc <--> Postgres
    CameraSvc <--> Postgres
    Auth <--> Postgres
    AuditSvc --> Postgres

    IncidentSvc --> Redis --> Dashboard
    CameraSvc --> Dashboard
    AnalyticsSvc --> Dashboard
    GISSvc --> Dashboard
    NotifySvc --> MobilePush
    Dashboard <--> Auth
```

## 3. Data Flow Summary (single frame → incident)

```mermaid
sequenceDiagram
    participant Cam as Camera
    participant Gw as Stream Gateway
    participant Bus as Kafka
    participant Models as AI Models (parallel)
    participant Agg as Confidence Aggregator
    participant DE as Decision Engine
    participant Inc as Incident Service
    participant Ev as Evidence Service
    participant Not as Notification Service

    Cam->>Gw: RTSP frames (continuous)
    Gw->>Bus: publish frame-event (sampled)
    Bus->>Models: fan-out to active models for this camera
    Models->>Agg: per-model results + confidence (per frame)
    Agg->>Agg: aggregate across N frames / T seconds
    Agg->>DE: aggregated multi-signal confidence
    DE->>DE: apply thresholds + agreement rules
    alt confidence + agreement satisfied
        DE->>Inc: create Incident (type, severity, confidence, explanation)
        Inc->>Ev: capture pre/during/post buffer, store to S3
        Inc->>Not: route per incident-type policy
        Not-->>Not: human confirmation OR auto-escalate
    else insufficient signal
        DE-->>Agg: discard / keep observing
    end
```

## 4. Service Boundaries

| Service | Responsibility | Maps to FRs |
|---|---|---|
| Auth Service | Authentication, RBAC, session/token issuance | FR-12 |
| Camera Management Service | Camera CRUD, health, zone/site mgmt | FR-1 |
| Stream Gateway | Protocol adapters (RTSP/ONVIF/WebRTC), frame sampling | FR-1 |
| AI Inference Services (one per model family) | Independently deployable model servers behind a common gRPC/REST contract | FR-2 |
| Confidence Aggregator | Temporal + multi-model fusion | FR-2.6 |
| AI Decision Engine | Threshold/agreement rules → incident creation | FR-3 |
| Incident Service | Incident lifecycle, state machine (open→confirmed→escalated→resolved/dismissed) | FR-3 |
| Evidence Service | Buffered clip capture, chain-of-custody storage | FR-4 |
| Reporting Service | PDF report generation | FR-5 |
| Notification Service | Multi-channel routing + delivery tracking | FR-6 |
| Analytics Service | Aggregated stats, dashboards | FR-7.6 |
| GIS Service | Map data, nearest-responder lookup, routing | FR-8 |
| Audit Service | Immutable audit trail of privileged actions | NFR-3 |

## 5. Deployment Topology

```mermaid
flowchart LR
    subgraph K8s["Kubernetes Cluster"]
        subgraph GPUPool["GPU Node Pool"]
            AIWorkers[AI Inference Pods<br/>autoscaled]
        end
        subgraph CPUPool["CPU Node Pool"]
            APIPods[API Service Pods]
            NotifyPods[Notification Pods]
            WebPods[Dashboard Pods]
        end
        Ingress[Ingress / API Gateway]
    end
    LB[Load Balancer] --> Ingress
    Ingress --> APIPods & WebPods & NotifyPods
    APIPods --> AIWorkers
    Postgres[(Managed PostgreSQL)]
    S3[(S3 / MinIO)]
    KafkaCluster[(Kafka Cluster)]
    RedisCluster[(Redis Cluster)]
    APIPods --> Postgres
    APIPods --> S3
    APIPods --> KafkaCluster
    APIPods --> RedisCluster
```

## 6. Folder Structure (Monorepo)

```
sentinel-ai/
├── docs/                          # PRD, SRS, architecture, ADRs
│   ├── 01_PRD.md
│   ├── 02_SRS.md
│   ├── 03_ARCHITECTURE.md
│   ├── 04_database_schema.sql
│   └── 05_ER_diagram.md
│
├── backend/
│   ├── services/
│   │   ├── auth-service/
│   │   │   ├── app/
│   │   │   │   ├── domain/            # entities, value objects
│   │   │   │   ├── application/       # use cases / services
│   │   │   │   ├── infrastructure/    # DB repos, external clients
│   │   │   │   └── api/               # FastAPI routers, schemas
│   │   │   ├── tests/
│   │   │   ├── Dockerfile
│   │   │   └── pyproject.toml
│   │   ├── camera-service/            # same internal layout pattern
│   │   ├── incident-service/
│   │   ├── evidence-service/
│   │   ├── reporting-service/
│   │   ├── notification-service/
│   │   ├── analytics-service/
│   │   ├── gis-service/
│   │   └── audit-service/
│   ├── ai-pipeline/
│   │   ├── inference-services/
│   │   │   ├── object-detection/
│   │   │   ├── pose-estimation/
│   │   │   ├── action-recognition/
│   │   │   ├── tracking/
│   │   │   ├── segmentation/
│   │   │   ├── face-recognition/      # opt-in, feature-flagged
│   │   │   ├── ocr/
│   │   │   └── audio-classification/
│   │   ├── aggregator/                # confidence aggregation + temporal analysis
│   │   ├── decision-engine/
│   │   └── model-registry/            # versioning, ONNX/TensorRT export configs
│   ├── shared/
│   │   ├── libs/                      # shared schemas, auth middleware, logging
│   │   └── proto/                     # gRPC contracts between AI services
│   └── gateway/
│       ├── stream-gateway/            # RTSP/ONVIF/WebRTC ingestion
│       └── api-gateway/               # public REST/GraphQL entrypoint
│
├── frontend/
│   ├── apps/
│   │   └── dashboard/                 # Next.js app
│   │       ├── app/                   # App Router pages
│   │       ├── components/
│   │       ├── lib/
│   │       ├── hooks/
│   │       └── public/
│   └── packages/
│       ├── ui/                        # shared shadcn-based component library
│       └── types/                     # shared TS types (generated from OpenAPI)
│
├── infra/
│   ├── docker/
│   │   └── docker-compose.yml         # local dev stack
│   ├── kubernetes/
│   │   ├── base/
│   │   └── overlays/{dev,staging,prod}/
│   ├── terraform/                     # cloud infra as code (optional path)
│   └── ci-cd/
│       └── github-actions/
│
├── tests/
│   ├── integration/
│   └── e2e/
│
├── scripts/                           # dev tooling, seed data, migration helpers
├── .env.example
├── docker-compose.yml
└── README.md
```

## 7. Key Design Decisions (ADR summary)

| Decision | Rationale |
|---|---|
| Microservices over monolith | Independent scaling of GPU-bound AI services vs. CPU-bound API services |
| Kafka for frame/result events | Decouples ingestion rate from inference throughput; enables replay for debugging |
| Redis for live fanout | Sub-second delivery of live alerts to dashboard via pub/sub |
| No single-frame alerting | Core false-positive mitigation requirement (FR-2.6) |
| Human-confirmation default | Safety/liability requirement (PRD §9) |
| Evidence store separate from OLTP DB | S3/MinIO better suited to large binary objects; Postgres holds metadata/pointers |
| Modular AI service contracts | Each model swappable independently (NFR-5) |

## 8. Next Phases

- **Phase 2** implements Auth, Camera, Incident, Evidence, Notification services against
  the schema in `04_database_schema.sql`.
- **Phase 3** implements the AI inference services and Decision Engine per the contracts
  defined here.
- **Phase 4** implements the Next.js dashboard consuming the Phase 2 APIs.
- **Phase 5** delivers Docker Compose (local), Kubernetes manifests, and CI/CD.
