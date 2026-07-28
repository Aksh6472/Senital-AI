"""
Camera Service — Application / Use-Case Layer.

Orchestrates camera CRUD, health checks, site/zone management,
and detection module configuration.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.camera_service.app.infrastructure.models import (
    CameraModel,
    SiteModel,
    ZoneModel,
)
from backend.services.camera_service.app.infrastructure.repositories import (
    CameraRepository,
    DetectionModuleRepository,
    SiteRepository,
    ZoneRepository,
)
from backend.services.shared.exceptions import BadRequestError, NotFoundError

# Valid stream types and statuses from the schema
VALID_STREAM_TYPES = {"rtsp", "onvif", "webcam", "upload"}
VALID_STATUSES = {"online", "offline", "degraded"}

# Default AI detection modules provisioned on camera creation
DEFAULT_DETECTION_MODULES = [
    {"module_code": "object_detection", "is_enabled": True, "config": {"confidence_threshold": 0.5}},
    {"module_code": "pose_estimation", "is_enabled": True, "config": {"confidence_threshold": 0.5}},
    {"module_code": "action_recognition", "is_enabled": True, "config": {"temporal_window_seconds": 5}},
    {"module_code": "tracking", "is_enabled": True, "config": {}},
    {"module_code": "segmentation", "is_enabled": False, "config": {}},
    {"module_code": "face_recognition", "is_enabled": False, "config": {"note": "opt-in, jurisdiction-gated"}},
    {"module_code": "ocr", "is_enabled": False, "config": {}},
    {"module_code": "audio_classification", "is_enabled": False, "config": {}},
]


class CameraService:
    """Camera management use cases."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.camera_repo = CameraRepository(db)
        self.module_repo = DetectionModuleRepository(db)
        self.site_repo = SiteRepository(db)
        self.zone_repo = ZoneRepository(db)

    # ── List Cameras ────────────────────────────────────────────

    async def list_cameras(
        self,
        site_id: UUID | None = None,
        zone_id: UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[CameraModel], int]:
        """Paginated camera listing with optional filters."""
        if status and status not in VALID_STATUSES:
            raise BadRequestError(
                detail=f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        return await self.camera_repo.list_cameras(
            site_id=site_id,
            zone_id=zone_id,
            status=status,
            offset=offset,
            limit=limit,
        )

    # ── Get Camera ──────────────────────────────────────────────

    async def get_camera(self, camera_id: UUID) -> CameraModel:
        camera = await self.camera_repo.get_by_id(camera_id)
        if camera is None:
            raise NotFoundError(entity="Camera", entity_id=str(camera_id))
        return camera

    # ── Create Camera ───────────────────────────────────────────

    async def create_camera(
        self,
        name: str,
        site_id: UUID,
        stream_type: str,
        stream_url: str | None = None,
        zone_id: UUID | None = None,
        latitude: str | None = None,
        longitude: str | None = None,
        resolution: str | None = None,
        fps: int | None = None,
        is_audio_enabled: bool = False,
    ) -> CameraModel:
        """Register a new camera and provision default detection modules."""
        # Validate stream type
        if stream_type not in VALID_STREAM_TYPES:
            raise BadRequestError(
                detail=f"Invalid stream_type '{stream_type}'. Must be one of: {', '.join(VALID_STREAM_TYPES)}"
            )

        # Validate site exists
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise NotFoundError(entity="Site", entity_id=str(site_id))

        # Validate zone exists (if provided)
        if zone_id:
            zone = await self.zone_repo.get_by_id(zone_id)
            if zone is None:
                raise NotFoundError(entity="Zone", entity_id=str(zone_id))
            if zone.site_id != site_id:
                raise BadRequestError(detail="Zone does not belong to the specified site.")

        # Create camera
        camera = CameraModel(
            name=name,
            site_id=site_id,
            zone_id=zone_id,
            stream_type=stream_type,
            stream_url=stream_url,
            latitude=latitude,
            longitude=longitude,
            resolution=resolution,
            fps=fps,
            is_audio_enabled=is_audio_enabled,
        )
        camera = await self.camera_repo.create(camera)

        # Provision default detection modules
        audio_modules = DEFAULT_DETECTION_MODULES.copy()
        if is_audio_enabled:
            # Enable audio classification by default if camera has audio
            for mod in audio_modules:
                if mod["module_code"] == "audio_classification":
                    mod["is_enabled"] = True
        await self.module_repo.bulk_upsert(camera.id, audio_modules)

        # Reload with relationships
        return await self.camera_repo.get_by_id(camera.id)

    # ── Update Camera ───────────────────────────────────────────

    async def update_camera(self, camera_id: UUID, **fields) -> CameraModel:
        """Partial update of camera attributes."""
        # Validate camera exists
        existing = await self.camera_repo.get_by_id(camera_id)
        if existing is None:
            raise NotFoundError(entity="Camera", entity_id=str(camera_id))

        # Validate stream_type if being updated
        if "stream_type" in fields and fields["stream_type"] not in VALID_STREAM_TYPES:
            raise BadRequestError(
                detail=f"Invalid stream_type '{fields['stream_type']}'. Must be one of: {', '.join(VALID_STREAM_TYPES)}"
            )

        # Validate zone if being updated
        if "zone_id" in fields and fields["zone_id"] is not None:
            zone = await self.zone_repo.get_by_id(fields["zone_id"])
            if zone is None:
                raise NotFoundError(entity="Zone", entity_id=str(fields["zone_id"]))
            if zone.site_id != existing.site_id:
                raise BadRequestError(detail="Zone does not belong to the camera's site.")

        # Filter out None values and unrecognized fields
        allowed = {
            "name", "stream_type", "stream_url", "zone_id", "latitude",
            "longitude", "resolution", "fps", "is_audio_enabled", "status",
        }
        update_fields = {k: v for k, v in fields.items() if k in allowed and v is not None}

        if not update_fields:
            return existing

        return await self.camera_repo.update(camera_id, **update_fields)

    # ── Delete Camera ───────────────────────────────────────────

    async def delete_camera(self, camera_id: UUID) -> bool:
        """Soft-delete a camera."""
        existing = await self.camera_repo.get_by_id(camera_id)
        if existing is None:
            raise NotFoundError(entity="Camera", entity_id=str(camera_id))
        return await self.camera_repo.soft_delete(camera_id)

    # ── Camera Health ───────────────────────────────────────────

    async def get_camera_health(self, camera_id: UUID) -> dict:
        """Return camera health snapshot."""
        camera = await self.camera_repo.get_by_id(camera_id)
        if camera is None:
            raise NotFoundError(entity="Camera", entity_id=str(camera_id))

        return {
            "camera_id": camera.id,
            "status": camera.status,
            "last_heartbeat_at": camera.last_heartbeat_at,
            "resolution": camera.resolution,
            "fps": camera.fps,
            "is_audio_enabled": camera.is_audio_enabled,
            "active_detection_modules": [
                m.module_code for m in camera.detection_modules if m.is_enabled
            ],
        }

    # ── Detection Modules ───────────────────────────────────────

    async def configure_detection_modules(
        self,
        camera_id: UUID,
        modules: list[dict],
    ) -> list:
        """Bulk replace detection modules for a camera."""
        camera = await self.camera_repo.get_by_id(camera_id)
        if camera is None:
            raise NotFoundError(entity="Camera", entity_id=str(camera_id))

        # Validate module codes
        valid_codes = {
            "object_detection", "pose_estimation", "action_recognition",
            "tracking", "segmentation", "face_recognition", "ocr",
            "audio_classification",
        }
        for mod in modules:
            if mod.get("module_code") not in valid_codes:
                raise BadRequestError(
                    detail=f"Invalid module_code '{mod.get('module_code')}'. Valid codes: {', '.join(sorted(valid_codes))}"
                )

        return await self.module_repo.bulk_upsert(camera_id, modules)
