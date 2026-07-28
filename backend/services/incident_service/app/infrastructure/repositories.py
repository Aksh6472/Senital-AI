"""
Incident Service — Database Repositories.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.incident_service.app.infrastructure.models import (
    EvidenceModel,
    IncidentModel,
    IncidentTypeModel,
)


class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, incident_id: UUID) -> IncidentModel | None:
        stmt = (
            select(IncidentModel)
            .options(
                selectinload(IncidentModel.incident_type),
                selectinload(IncidentModel.evidence),
            )
            .where(IncidentModel.id == incident_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_incidents(
        self,
        incident_type_code: str | None = None,
        camera_id: UUID | None = None,
        status: str | None = None,
        severity: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[IncidentModel], int]:
        base = select(IncidentModel)
        count_base = select(func.count(IncidentModel.id))

        if incident_type_code:
            base = base.where(IncidentModel.incident_type_code == incident_type_code)
            count_base = count_base.where(IncidentModel.incident_type_code == incident_type_code)
        if camera_id:
            base = base.where(IncidentModel.camera_id == camera_id)
            count_base = count_base.where(IncidentModel.camera_id == camera_id)
        if status:
            base = base.where(IncidentModel.status == status)
            count_base = count_base.where(IncidentModel.status == status)
        if severity:
            base = base.where(IncidentModel.severity == severity)
            count_base = count_base.where(IncidentModel.severity == severity)

        total_result = await self.db.execute(count_base)
        total = total_result.scalar() or 0

        stmt = (
            base
            .options(
                selectinload(IncidentModel.incident_type),
                selectinload(IncidentModel.evidence),
            )
            .order_by(IncidentModel.detected_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def update_status(
        self,
        incident_id: UUID,
        new_status: str,
        user_id: UUID | None = None,
    ) -> IncidentModel | None:
        """Update incident status and relevant timestamps."""
        updates = {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc),
        }
        
        if new_status == "confirmed":
            updates["confirmed_by"] = user_id
            updates["confirmed_at"] = datetime.now(timezone.utc)
        elif new_status in ("resolved", "dismissed", "false_positive"):
            updates["resolved_at"] = datetime.now(timezone.utc)
            
        stmt = (
            update(IncidentModel)
            .where(IncidentModel.id == incident_id)
            .values(**updates)
        )
        await self.db.execute(stmt)
        return await self.get_by_id(incident_id)


class EvidenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, evidence_id: UUID) -> EvidenceModel | None:
        stmt = select(EvidenceModel).where(EvidenceModel.id == evidence_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_incident(self, incident_id: UUID) -> list[EvidenceModel]:
        stmt = (
            select(EvidenceModel)
            .where(EvidenceModel.incident_id == incident_id)
            .order_by(EvidenceModel.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
