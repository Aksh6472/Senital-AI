"""
Notification Service — FastAPI Router.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification_service.app.api.schemas import (
    NotificationPolicyResponse,
    NotificationResponse,
    UpdateNotificationPolicyRequest,
)
from backend.services.notification_service.app.application.notification_service import (
    NotificationService,
)
from backend.services.shared.auth_middleware import require_permission
from backend.services.shared.database import get_db

router = APIRouter(tags=["Notifications"])


@router.get(
    "/notification-policies",
    response_model=list[NotificationPolicyResponse],
    dependencies=[Depends(require_permission("policy:read"))],
)
async def list_policies(
    site_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    policies = await svc.list_policies(site_id)
    return [NotificationPolicyResponse.model_validate(p) for p in policies]


@router.put(
    "/notification-policies/{policy_id}",
    response_model=NotificationPolicyResponse,
    dependencies=[Depends(require_permission("policy:write"))],
)
async def update_policy(
    policy_id: UUID,
    body: UpdateNotificationPolicyRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    update_data = body.model_dump(exclude_unset=True)
    policy = await svc.update_policy(policy_id, **update_data)
    return NotificationPolicyResponse.model_validate(policy)


@router.get(
    "/incidents/{incident_id}/notifications",
    response_model=list[NotificationResponse],
    dependencies=[Depends(require_permission("incident:read"))],
)
async def get_incident_notifications(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    notifications = await svc.list_notifications(incident_id)
    return [NotificationResponse.model_validate(n) for n in notifications]
