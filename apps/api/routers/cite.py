"""
Mourya Scholarium — Citation Router
POST /api/v1/cite/format — format citations for given sources
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from models import User
from dependencies import get_current_user
from agents.citation import CitationAgent

router = APIRouter()
citation_agent = CitationAgent()


class FormatRequest(BaseModel):
    sources: List[Dict[str, Any]]
    style: str = "APA7"


@router.post("/format")
async def format_citations(
    req: FormatRequest,
    user: User = Depends(get_current_user),
):
    bibliography = citation_agent._build_bibliography(req.sources)
    return {"bibliography": bibliography, "style": req.style, "count": len(bibliography)}
