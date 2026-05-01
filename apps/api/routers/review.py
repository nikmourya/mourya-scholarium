"""
Mourya Scholarium — Review Router
POST /api/v1/review — start a literature review workflow
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from models import User
from dependencies import get_current_user

router = APIRouter()


class ReviewRequest(BaseModel):
    topic: str
    review_type: str = "narrative"
    discipline: Optional[str] = None
    max_sources: int = 30
    project_id: Optional[str] = None


@router.post("")
async def start_review(
    req: ReviewRequest,
    user: User = Depends(get_current_user),
):
    # For MVP, redirect to the write endpoint with literature_review mode
    return {
        "message": "Use POST /api/v1/write with writing_mode='literature_review' for review generation.",
        "review_type": req.review_type,
        "topic": req.topic,
    }
