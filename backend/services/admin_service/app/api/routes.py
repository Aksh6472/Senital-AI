"""
Admin & Audit Service — FastAPI Router.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.auth_service.app.infrastructure.models import RoleModel, UserModel
from backend.services.auth_service.app.api.schemas import RoleResponse, UserResponse
from backend.services.shared.auth_middleware import require_permission
from backend.services.shared.database import get_db
from backend.services.shared.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter(tags=["Admin & Audit"])


@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse],
    dependencies=[Depends(require_permission("user:read"))],
)
async def list_users(
    response: Response,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    
    count_stmt = select(func.count(UserModel.id)).where(UserModel.deleted_at.is_(None))
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(UserModel)
        .where(UserModel.deleted_at.is_(None))
        .options(selectinload(UserModel.role), selectinload(UserModel.organization))
        .order_by(UserModel.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    items = list((await db.execute(stmt)).scalars().all())

    return paginate(
        items=[UserResponse.model_validate(u) for u in items],
        total=total,
        params=pagination,
        response=response,
    )


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("role:read"))],
)
async def list_roles(
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    from backend.services.auth_service.app.infrastructure.models import RolePermissionModel
    
    stmt = (
        select(RoleModel)
        .options(
            selectinload(RoleModel.role_permissions)
            .selectinload(RolePermissionModel.permission)
        )
        .order_by(RoleModel.name)
    )
    roles = list((await db.execute(stmt)).scalars().all())
    
    # Map role_permissions back to permissions list for the schema
    for role in roles:
        role.permissions = [rp.permission for rp in role.role_permissions]
        
    return [RoleResponse.model_validate(r) for r in roles]
