"""
Camera Service — Database Repositories.

Async SQLAlchemy repos for cameras, sites, zones, and detection modules.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.camera_service.app.infrastructure.models import (
    CameraDetectionModuleModel,
    CameraModel,
    SiteModel,
    ZoneModel,
)


# ── Camera Repository ──────────────────────────────────────────

class CameraRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, camera_id: UUID) -> CameraModel | None:
        """Fetch camera with site, zone, and detection modules."""
        stmt = (
            select(CameraModel)
            .options(
                selectinload(CameraModel.site),
                selectinload(CameraModel.zone),
                selectinload(CameraModel.detection_modules),
            )
            .where(CameraModel.id == camera_id)
            .where(CameraModel.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_cameras(
        self,
        site_id: UUID | None = None,
        zone_id: UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[CameraModel], int]:
        """Paginated camera list with optional filters. Returns (items, total)."""
        base = select(CameraModel).where(CameraModel.deleted_at.is_(None))
        count_base = select(func.count(CameraModel.id)).where(CameraModel.deleted_at.is_(None))

        if site_id:
            base = base.where(CameraModel.site_id == site_id)
            count_base = count_base.where(CameraModel.site_id == site_id)
        if zone_id:
            base = base.where(CameraModel.zone_id == zone_id)
            count_base = count_base.where(CameraModel.zone_id == zone_id)
        if status:
            base = base.where(CameraModel.status == status)
            count_base = count_base.where(CameraModel.status == status)

        total_result = await self.db.execute(count_base)
        total = total_result.scalar() or 0

        stmt = (
            base
            .options(
                selectinload(CameraModel.site),
                selectinload(CameraModel.zone),
                selectinload(CameraModel.detection_modules),
            )
            .order_by(CameraModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def create(self, camera: CameraModel) -> CameraModel:
        self.db.add(camera)
        await self.db.flush()
        return camera

    async def update(self, camera_id: UUID, **fields) -> CameraModel | None:
        """Partial update of camera fields."""
        fields["updated_at"] = datetime.now(timezone.utc)
        stmt = (
            update(CameraModel)
            .where(CameraModel.id == camera_id)
            .where(CameraModel.deleted_at.is_(None))
            .values(**fields)
            .returning(CameraModel)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return await self.get_by_id(camera_id)

    async def soft_delete(self, camera_id: UUID) -> bool:
        """Soft-delete by setting deleted_at."""
        stmt = (
            update(CameraModel)
            .where(CameraModel.id == camera_id)
            .where(CameraModel.deleted_at.is_(None))
            .values(deleted_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def update_heartbeat(self, camera_id: UUID, status: str = "online") -> None:
        """Update camera heartbeat timestamp and status."""
        stmt = (
            update(CameraModel)
            .where(CameraModel.id == camera_id)
            .values(
                last_heartbeat_at=datetime.now(timezone.utc),
                status=status,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.db.execute(stmt)


# ── Detection Module Repository ─────────────────────────────────

class DetectionModuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_for_camera(self, camera_id: UUID) -> list[CameraDetectionModuleModel]:
        stmt = (
            select(CameraDetectionModuleModel)
            .where(CameraDetectionModuleModel.camera_id == camera_id)
            .order_by(CameraDetectionModuleModel.module_code)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def bulk_upsert(
        self,
        camera_id: UUID,
        modules: list[dict],
    ) -> list[CameraDetectionModuleModel]:
        """
        Replace all detection modules for a camera.
        Deletes existing modules, then inserts the new set.
        """
        # Delete existing
        await self.db.execute(
            delete(CameraDetectionModuleModel)
            .where(CameraDetectionModuleModel.camera_id == camera_id)
        )

        # Insert new
        new_models = []
        for mod in modules:
            m = CameraDetectionModuleModel(
                camera_id=camera_id,
                module_code=mod["module_code"],
                is_enabled=mod.get("is_enabled", True),
                config=mod.get("config", {}),
            )
            self.db.add(m)
            new_models.append(m)

        await self.db.flush()
        return new_models


# ── Site Repository ─────────────────────────────────────────────

class SiteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, site_id: UUID) -> SiteModel | None:
        stmt = (
            select(SiteModel)
            .options(selectinload(SiteModel.zones))
            .where(SiteModel.id == site_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(self, org_id: UUID) -> list[SiteModel]:
        stmt = (
            select(SiteModel)
            .where(SiteModel.organization_id == org_id)
            .order_by(SiteModel.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, site: SiteModel) -> SiteModel:
        self.db.add(site)
        await self.db.flush()
        return site


# ── Zone Repository ─────────────────────────────────────────────

class ZoneRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, zone_id: UUID) -> ZoneModel | None:
        stmt = select(ZoneModel).where(ZoneModel.id == zone_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_site(self, site_id: UUID) -> list[ZoneModel]:
        stmt = (
            select(ZoneModel)
            .where(ZoneModel.site_id == site_id)
            .order_by(ZoneModel.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, zone: ZoneModel) -> ZoneModel:
        self.db.add(zone)
        await self.db.flush()
        return zone
