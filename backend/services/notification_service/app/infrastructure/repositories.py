"""
Notification Service — Database Repositories.
"""

from __future__ import annotations

from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification_service.app.infrastructure.models import (
    NotificationModel,
    NotificationPolicyModel,
)


class NotificationPolicyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_policy(self, site_id: UUID, incident_type_code: str) -> NotificationPolicyModel | None:
        stmt = (
            select(NotificationPolicyModel)
            .where(NotificationPolicyModel.site_id == site_id)
            .where(NotificationPolicyModel.incident_type_code == incident_type_code)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_policies(self, site_id: UUID | None = None) -> list[NotificationPolicyModel]:
        stmt = select(NotificationPolicyModel)
        if site_id:
            stmt = stmt.where(NotificationPolicyModel.site_id == site_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_policy(
        self,
        policy_id: UUID,
        **fields
    ) -> NotificationPolicyModel | None:
        stmt = (
            update(NotificationPolicyModel)
            .where(NotificationPolicyModel.id == policy_id)
            .values(**fields)
            .returning(NotificationPolicyModel)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_incident(self, incident_id: UUID) -> list[NotificationModel]:
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.incident_id == incident_id)
            .order_by(NotificationModel.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, notification: NotificationModel) -> NotificationModel:
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def update_status(
        self,
        notification_id: UUID,
        status: str,
        error_message: str | None = None
    ) -> None:
        updates = {"status": status}
        now = datetime.now(timezone.utc)
        
        if status == "sent":
            updates["sent_at"] = now
        elif status == "delivered":
            updates["delivered_at"] = now
        elif status == "failed":
            updates["error_message"] = error_message
            
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .values(**updates)
        )
        await self.db.execute(stmt)
