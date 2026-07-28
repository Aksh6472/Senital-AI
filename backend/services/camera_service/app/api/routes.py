"""
Camera Service — FastAPI Router.

Endpoints:
    GET    /api/v1/cameras                            → List cameras
    POST   /api/v1/cameras                            → Register new camera
    GET    /api/v1/cameras/{id}                        → Camera detail
    PATCH  /api/v1/cameras/{id}                        → Update camera
    DELETE /api/v1/cameras/{id}                        → Soft-delete camera
    GET    /api/v1/cameras/{id}/health                 → Camera health
    PUT    /api/v1/cameras/{id}/detection-modules      → Configure AI modules
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.camera_service.app.api.schemas import (
    CameraHealthResponse,
    CameraResponse,
    ConfigureDetectionModulesRequest,
    CreateCameraRequest,
    DetectionModuleResponse,
    UpdateCameraRequest,
)
from backend.services.camera_service.app.application.camera_service import CameraService
from backend.services.shared.auth_middleware import require_permission
from backend.services.shared.database import get_db
from backend.services.shared.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter(prefix="/cameras", tags=["Camera Management"])


# ── GET /cameras ────────────────────────────────────────────────

@router.get(
    "",
    response_model=PaginatedResponse[CameraResponse],
    dependencies=[Depends(require_permission("camera:read"))],
)
async def list_cameras(
    response: Response,
    site_id: UUID | None = None,
    zone_id: UUID | None = None,
    status: str | None = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """List cameras with optional filters (site, zone, status)."""
    svc = CameraService(db)
    items, total = await svc.list_cameras(
        site_id=site_id,
        zone_id=zone_id,
        status=status,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return paginate(
        items=[CameraResponse.model_validate(c) for c in items],
        total=total,
        params=pagination,
        response=response,
    )


# ── POST /cameras ──────────────────────────────────────────────

@router.post(
    "",
    response_model=CameraResponse,
    status_code=201,
    dependencies=[Depends(require_permission("camera:write"))],
)
async def create_camera(
    body: CreateCameraRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new camera and provision default detection modules."""
    svc = CameraService(db)
    camera = await svc.create_camera(
        name=body.name,
        site_id=body.site_id,
        stream_type=body.stream_type,
        stream_url=body.stream_url,
        zone_id=body.zone_id,
        latitude=body.latitude,
        longitude=body.longitude,
        resolution=body.resolution,
        fps=body.fps,
        is_audio_enabled=body.is_audio_enabled,
    )
    return CameraResponse.model_validate(camera)


# ── GET /cameras/{id} ──────────────────────────────────────────

@router.get(
    "/{camera_id}",
    response_model=CameraResponse,
    dependencies=[Depends(require_permission("camera:read"))],
)
async def get_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full camera detail including site, zone, and detection modules."""
    svc = CameraService(db)
    camera = await svc.get_camera(camera_id)
    return CameraResponse.model_validate(camera)


# ── PATCH /cameras/{id} ────────────────────────────────────────

@router.patch(
    "/{camera_id}",
    response_model=CameraResponse,
    dependencies=[Depends(require_permission("camera:write"))],
)
async def update_camera(
    camera_id: UUID,
    body: UpdateCameraRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update camera configuration (partial update)."""
    svc = CameraService(db)
    update_data = body.model_dump(exclude_unset=True)
    camera = await svc.update_camera(camera_id, **update_data)
    return CameraResponse.model_validate(camera)


# ── DELETE /cameras/{id} ───────────────────────────────────────

@router.delete(
    "/{camera_id}",
    status_code=204,
    dependencies=[Depends(require_permission("camera:delete"))],
)
async def delete_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a camera (sets deleted_at timestamp)."""
    svc = CameraService(db)
    await svc.delete_camera(camera_id)


# ── GET /cameras/{id}/health ───────────────────────────────────

@router.get(
    "/{camera_id}/health",
    response_model=CameraHealthResponse,
    dependencies=[Depends(require_permission("camera:read"))],
)
async def get_camera_health(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get live health status for a camera."""
    svc = CameraService(db)
    health = await svc.get_camera_health(camera_id)
    return CameraHealthResponse(**health)


# ── PUT /cameras/{id}/detection-modules ────────────────────────

@router.put(
    "/{camera_id}/detection-modules",
    response_model=list[DetectionModuleResponse],
    dependencies=[Depends(require_permission("camera:write"))],
)
async def configure_detection_modules(
    camera_id: UUID,
    body: ConfigureDetectionModulesRequest,
    db: AsyncSession = Depends(get_db),
):
    """Bulk-replace the active AI detection modules for a camera."""
    svc = CameraService(db)
    modules = await svc.configure_detection_modules(
        camera_id=camera_id,
        modules=[m.model_dump() for m in body.modules],
    )
    return [DetectionModuleResponse.model_validate(m) for m in modules]
