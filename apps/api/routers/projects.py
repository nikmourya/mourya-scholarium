"""
Mourya Scholarium — Projects Router
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, Project
from dependencies import get_current_user

router = APIRouter()


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    discipline: Optional[str] = None
    topic: Optional[str] = None
    project_type: Optional[str] = None


@router.post("")
async def create_project(
    req: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = Project(user_id=user.id, **req.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return {"project_id": str(project.id), "title": project.title}


@router.get("")
async def list_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.user_id == user.id).order_by(Project.updated_at.desc())
    )
    projects = result.scalars().all()
    return {
        "projects": [
            {
                "id": str(p.id), "title": p.title, "description": p.description,
                "project_type": p.project_type, "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
    }
