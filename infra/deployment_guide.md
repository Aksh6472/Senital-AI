# Sentinel AI — DevOps & Deployment Guide

This guide provides the complete instructions to deploy the Sentinel AI platform locally using Docker Compose, or to a Kubernetes cluster using the provided manifests.

---

## 1. Local Development Stack (Docker Compose)

The local stack spins up all five microservices, the Next.js frontend, and the supporting infrastructure: PostgreSQL (with PostGIS), Redis, MinIO, and an Nginx Gateway.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### Quick Start
1. **Navigate to the project root** where `docker-compose.yml` is located.
2. **Build and start the containers** in detached mode:
   ```bash
   docker compose up --build -d
   ```
3. **Verify the container status**:
   ```bash
   docker compose ps
   ```
   You should see 10 containers running successfully.

### Service Ports Mapping
- **Nginx API Gateway**: [http://localhost:8000](http://localhost:8000) (Routes requests starting with `/api/v1/` to the matching microservice)
- **Frontend Dashboard**: [http://localhost:3001](http://localhost:3001) (Consumes the API via the Gateway)
- **PostgreSQL Database**: Port `5432` on `localhost` (credentials: user `sentinel`, password `sentinel`, db `sentinel_ai`)
- **MinIO S3 Console**: [http://localhost:9001](http://localhost:9001) (API on port `9000`, credentials: user `minioadmin`, password `minioadmin`)
- **Redis Cache**: Port `6379` on `localhost`

### Default Seeded Users
The database is pre-seeded with the following roles, default camera, and default users (passwords are hashed via PostgreSQL `pgcrypto` crypt function on startup):
1. **System Administrator**:
   - **Email**: `admin@sentinel.ai`
   - **Password**: `adminpassword`
2. **Control Room Operator**:
   - **Email**: `operator@sentinel.ai`
   - **Password**: `operatorpassword`

### Verification & Testing APIs
You can test the API routing using curl:
```bash
# Login request to retrieve the JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@sentinel.ai", "password": "adminpassword"}'
```

### Shutdown
To stop and remove all containers, networks, and volumes:
```bash
docker compose down -v
```

---

## 2. Production Deployment (Kubernetes)

The Kubernetes manifests are configured under the `infra/kubernetes/base` directory and deploy to the `sentinel-ai` namespace.

### Prerequisites
- Access to a Kubernetes Cluster (e.g., Minikube, GKE, EKS, AKS).
- `kubectl` configured to connect to your cluster.
- Nginx Ingress Controller installed on the cluster.

### Step-by-Step Deployment
1. **Create the Namespace**:
   ```bash
   kubectl apply -f infra/kubernetes/base/namespace.yaml
   ```

2. **Deploy Configurations & Secrets**:
   > [!IMPORTANT]
   > For production, update the raw values in `infra/kubernetes/base/secrets.yaml` and re-encode them in base64.
   ```bash
   kubectl apply -f infra/kubernetes/base/configmap.yaml
   kubectl apply -f infra/kubernetes/base/secrets.yaml
   ```

3. **Deploy Core Databases & Stores**:
   This spins up Postgres (PostGIS), Redis, MinIO, and executes the bucket initialization job.
   ```bash
   kubectl apply -f infra/kubernetes/base/postgres.yaml
   kubectl apply -f infra/kubernetes/base/redis.yaml
   kubectl apply -f infra/kubernetes/base/minio.yaml
   ```
   *Wait for the databases to become healthy:*
   ```bash
   kubectl get pods -n sentinel-ai -w
   ```

4. **Deploy Microservices & Frontend**:
   Build the backend image (`sentinel-backend:latest`) and frontend image (`sentinel-frontend:latest`) and push them to your cluster's registry before applying these manifests:
   ```bash
   kubectl apply -f infra/kubernetes/base/services.yaml
   ```

5. **Deploy Routing Ingress**:
   Ensure you have an Ingress controller configured.
   ```bash
   kubectl apply -f infra/kubernetes/base/ingress.yaml
   ```

6. **Access the Application**:
   Map `sentinel-ai.local` in your `/etc/hosts` file (or equivalent Windows hosts file) to your Kubernetes Ingress IP:
   ```text
   <INGRESS_LOADBALANCER_IP> sentinel-ai.local
   ```
   Open [http://sentinel-ai.local](http://sentinel-ai.local) in your browser.

---

## 3. Database Seeding Modification
If you wish to modify the default seed records or passwords before deploying:
- **Local Compose**: Edit [seed.sql](file:///c:/Users/welcome/OneDrive/New%20folder/Senital%20AI/infra/docker/seed.sql) before executing `docker compose up`.
- **Kubernetes**: Edit the `postgres-init-config` ConfigMap in [postgres.yaml](file:///c:/Users/welcome/OneDrive/New%20folder/Senital%20AI/infra/kubernetes/base/postgres.yaml). You can alter the default emails, camera names, and passwords.

---

## 4. Continuous Integration (GitHub Actions)

The CI/CD pipeline is defined in [ci.yml](file:///c:/Users/welcome/OneDrive/New%20folder/Senital%20AI/.github/workflows/ci.yml).
- **Triggers**: On every push or pull request to the `main` or `develop` branches.
- **Workflow Steps**:
  1. Installs Python dependencies and runs `ruff` / `black` linting.
  2. Runs Python pytest unit and benchmark suites.
  3. Installs Node.js dependencies, lints, and builds the frontend.
  4. Runs dry-run Docker builds for both `backend/Dockerfile` and `frontend/Dockerfile` to prevent broken images from slipping into registries.
