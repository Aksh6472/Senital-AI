"""
Incident Service — Application Layer.

Incident lifecycle state machine and evidence retrieval.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.incident_service.app.infrastructure.models import (
    EvidenceModel,
    IncidentModel,
)
from backend.services.incident_service.app.infrastructure.repositories import (
    EvidenceRepository,
    IncidentRepository,
)
from backend.services.shared.exceptions import InvalidStateTransitionError, NotFoundError


class IncidentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.incident_repo = IncidentRepository(db)

    async def list_incidents(
        self,
        incident_type_code: str | None = None,
        camera_id: UUID | None = None,
        status: str | None = None,
        severity: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[IncidentModel], int]:
        return await self.incident_repo.list_incidents(
            incident_type_code, camera_id, status, severity, offset, limit
        )

    async def get_incident(self, incident_id: UUID) -> IncidentModel:
        incident = await self.incident_repo.get_by_id(incident_id)
        if incident is None:
            raise NotFoundError("Incident", str(incident_id))
        return incident

    async def confirm_incident(self, incident_id: UUID, user_id: UUID) -> IncidentModel:
        """State transition: open -> confirmed."""
        incident = await self.get_incident(incident_id)
        if incident.status != "open":
            raise InvalidStateTransitionError(incident.status, "confirm")
            
        return await self.incident_repo.update_status(incident_id, "confirmed", user_id)

    async def dismiss_incident(self, incident_id: UUID, user_id: UUID, is_false_positive: bool = False) -> IncidentModel:
        """State transition: open -> dismissed/false_positive."""
        incident = await self.get_incident(incident_id)
        if incident.status not in ("open", "confirmed"):
            raise InvalidStateTransitionError(incident.status, "dismiss")
            
        new_status = "false_positive" if is_false_positive else "dismissed"
        return await self.incident_repo.update_status(incident_id, new_status, user_id)

    async def escalate_incident(self, incident_id: UUID, user_id: UUID) -> IncidentModel:
        """State transition: confirmed -> escalated. (Triggers notification logic later)"""
        incident = await self.get_incident(incident_id)
        if incident.status != "confirmed":
            # Can also auto-escalate from open, but manual usually requires confirmation first
            if incident.status != "open":
                 raise InvalidStateTransitionError(incident.status, "escalate")
                 
        return await self.incident_repo.update_status(incident_id, "escalated", user_id)


class EvidenceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.incident_repo = IncidentRepository(db)

    async def list_evidence(self, incident_id: UUID) -> list[EvidenceModel]:
        incident = await self.incident_repo.get_by_id(incident_id)
        if incident is None:
             raise NotFoundError("Incident", str(incident_id))
             
        return await self.evidence_repo.list_by_incident(incident_id)

    async def get_evidence(self, evidence_id: UUID) -> EvidenceModel:
        evidence = await self.evidence_repo.get_by_id(evidence_id)
        if evidence is None:
            raise NotFoundError("Evidence", str(evidence_id))
        return evidence
