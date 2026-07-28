"""
Incident Service — FastAPI Router.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.incident_service.app.api.schemas import (
    DismissIncidentRequest,
    EvidenceResponse,
    IncidentResponse,
)
from backend.services.incident_service.app.application.incident_service import (
    EvidenceService,
    IncidentService,
)
from backend.services.shared.auth_middleware import get_current_user, require_permission
from backend.services.shared.database import get_db
from backend.services.shared.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter(prefix="/incidents", tags=["Incidents & Evidence"])


@router.get(
    "",
    response_model=PaginatedResponse[IncidentResponse],
    dependencies=[Depends(require_permission("incident:read"))],
)
async def list_incidents(
    response: Response,
    incident_type: str | None = None,
    camera_id: UUID | None = None,
    status: str | None = None,
    severity: str | None = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    svc = IncidentService(db)
    items, total = await svc.list_incidents(
        incident_type_code=incident_type,
        camera_id=camera_id,
        status=status,
        severity=severity,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return paginate(
        items=[IncidentResponse.model_validate(i) for i in items],
        total=total,
        params=pagination,
        response=response,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    dependencies=[Depends(require_permission("incident:read"))],
)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    svc = IncidentService(db)
    incident = await svc.get_incident(incident_id)
    return IncidentResponse.model_validate(incident)


@router.post(
    "/{incident_id}/confirm",
    response_model=IncidentResponse,
    dependencies=[Depends(require_permission("incident:write"))],
)
async def confirm_incident(
    incident_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = IncidentService(db)
    incident = await svc.confirm_incident(incident_id, current_user.id)
    return IncidentResponse.model_validate(incident)


@router.post(
    "/{incident_id}/dismiss",
    response_model=IncidentResponse,
    dependencies=[Depends(require_permission("incident:write"))],
)
async def dismiss_incident(
    incident_id: UUID,
    body: DismissIncidentRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = IncidentService(db)
    incident = await svc.dismiss_incident(
        incident_id,
        current_user.id,
        is_false_positive=body.is_false_positive
    )
    return IncidentResponse.model_validate(incident)


@router.post(
    "/{incident_id}/escalate",
    response_model=IncidentResponse,
    dependencies=[Depends(require_permission("incident:write"))],
)
async def escalate_incident(
    incident_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = IncidentService(db)
    incident = await svc.escalate_incident(incident_id, current_user.id)
    return IncidentResponse.model_validate(incident)


@router.get(
    "/{incident_id}/evidence",
    response_model=list[EvidenceResponse],
    dependencies=[Depends(require_permission("incident:read"))],
)
async def list_evidence(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    svc = EvidenceService(db)
    evidence = await svc.list_evidence(incident_id)
    return [EvidenceResponse.model_validate(e) for e in evidence]


# For single evidence item retrieval
evidence_router = APIRouter(prefix="/evidence", tags=["Evidence"])

@evidence_router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
    dependencies=[Depends(require_permission("incident:read"))],
)
async def get_evidence(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    svc = EvidenceService(db)
    evidence = await svc.get_evidence(evidence_id)
    return EvidenceResponse.model_validate(evidence)
