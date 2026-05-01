"""
Mourya Scholarium — Evidence Router
GET /api/v1/evidence/{session_id} — get evidence traces for a session
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, WritingSession
from dependencies import get_current_user

router = APIRouter()


@router.get("/{session_id}")
async def get_evidence_traces(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WritingSession).where(
            WritingSession.id == uuid.UUID(session_id),
            WritingSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    return {
        "session_id": str(session.id),
        "integrity_status": session.integrity_status,
        "integrity_report": session.integrity_report,
        "sources_used": session.sources_used,
    }
