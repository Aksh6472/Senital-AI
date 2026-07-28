"""
Notification Service — Application Logic.

Evaluates policies and orchestrates sending via channels.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification_service.app.infrastructure.models import (
    NotificationModel,
    NotificationPolicyModel,
)
from backend.services.notification_service.app.infrastructure.repositories import (
    NotificationPolicyRepository,
    NotificationRepository,
)
from backend.services.shared.exceptions import NotFoundError


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.policy_repo = NotificationPolicyRepository(db)
        self.notification_repo = NotificationRepository(db)

    async def list_policies(self, site_id: UUID | None = None) -> list[NotificationPolicyModel]:
        return await self.policy_repo.list_policies(site_id)

    async def update_policy(self, policy_id: UUID, **fields) -> NotificationPolicyModel:
        policy = await self.policy_repo.update_policy(policy_id, **fields)
        if policy is None:
             raise NotFoundError("NotificationPolicy", str(policy_id))
        return policy

    async def list_notifications(self, incident_id: UUID) -> list[NotificationModel]:
        return await self.notification_repo.list_by_incident(incident_id)

    async def trigger_incident_notifications(self, incident_id: UUID, site_id: UUID, incident_type: str, confidence: float):
        """
        Evaluate policy for an incident.
        If requires_confirmation=False or (auto_escalate_threshold <= confidence), send.
        Otherwise, log pending human review.
        """
        policy = await self.policy_repo.get_policy(site_id, incident_type)
        if not policy:
            return # No policy defined
            
        should_send = False
        if not policy.requires_confirmation:
            should_send = True
        elif policy.auto_escalate_threshold and confidence >= float(policy.auto_escalate_threshold):
            should_send = True
            
        if should_send:
            # Create notification records and fan out to channel adapters
            for channel in policy.channels:
                for recipient in policy.recipients:
                    notif = NotificationModel(
                        incident_id=incident_id,
                        channel=channel,
                        recipient=recipient.get("contact_id", "unknown"),
                        status="pending"
                    )
                    await self.notification_repo.create(notif)
                    # In a real system, we'd dispatch to a task queue (Celery/Kafka) here
                    # For v1, we just mark as sent to simulate the adapter success
                    asyncio.create_task(self._mock_send(notif.id))
                    
    async def _mock_send(self, notification_id: UUID):
        """Simulate async sending via external API."""
        await asyncio.sleep(0.5)
        # Note: in a real background task, we need a new DB session.
        # This is just a placeholder logic to represent the channel adapter.
        pass
