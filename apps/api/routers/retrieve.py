"""
Mourya Scholarium — Retrieve, Cite, Review, Evidence Routers
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from dependencies import get_current_user
from agents.retrieval import RetrievalAgent
from agents.citation import CitationAgent

# ── Retrieve Router ──
router = APIRouter()
retrieval_agent = RetrievalAgent()


class RetrieveRequest(BaseModel):
    query: str
    discipline: Optional[str] = None
    max_results: int = 20


@router.post("")
async def retrieve_sources(
    req: RetrieveRequest,
    user: User = Depends(get_current_user),
):
    result = await retrieval_agent.execute({
        "user_prompt": req.query,
        "max_sources": req.max_results,
        "user_profile": {"discipline": req.discipline or ""},
    })
    return result.payload
