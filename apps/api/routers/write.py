"""
Mourya Scholarium — Write Router
POST /api/v1/write                     — submit writing request (full orchestration)
GET  /api/v1/write/{session_id}        — get session result
POST /api/v1/write/{session_id}/feedback — submit feedback
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, UserProfile, StyleSignature, WritingSession, FeedbackSignal
from dependencies import get_current_user
from agents.orchestrator import OrchestratorAgent
from agents.pedagogy import PedagogyAgent
from agents.style_learning import StyleLearningAgent
from agents.retrieval import RetrievalAgent
from agents.ml_systems import MLSystemsAgent
from agents.literature_review import LiteratureReviewAgent
from agents.writing import WritingAgent
from agents.citation import CitationAgent
from agents.integrity import IntegrityAgent
from agents.evaluation import EvaluationAgent

router = APIRouter()


class WriteRequest(BaseModel):
    project_id: Optional[str] = None
    writing_mode: str = "write_from_prompt"
    prompt: str
    input_text: Optional[str] = None
    additional_instructions: Optional[str] = None
    max_sources: int = 20
    review_type: str = "narrative"


class FeedbackRequest(BaseModel):
    signal_type: str   # accept | edit | reject
    edit_diff: Optional[str] = None
    comments: Optional[str] = None


def _build_orchestrator() -> OrchestratorAgent:
    agents = {
        "pedagogy": PedagogyAgent(),
        "style_learning": StyleLearningAgent(),
        "retrieval": RetrievalAgent(),
        "ml_systems": MLSystemsAgent(),
        "literature_review": LiteratureReviewAgent(),
        "writing": WritingAgent(),
        "citation": CitationAgent(),
        "integrity": IntegrityAgent(),
        "evaluation": EvaluationAgent(),
    }
    return OrchestratorAgent(agents)


@router.post("")
async def submit_write_request(
    req: WriteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Load user profile
    prof_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = prof_result.scalar_one_or_none()
    profile_dict = {}
    if profile:
        profile_dict = {
            "english_level": profile.english_level,
            "academic_level": profile.academic_level,
            "discipline": profile.discipline,
            "target_output_level": profile.target_output_level,
            "preservation_priorities": profile.preservation_priorities,
            "improvement_targets": profile.improvement_targets,
        }

    # Load style signature
    sig_result = await db.execute(select(StyleSignature).where(StyleSignature.user_id == user.id))
    sig = sig_result.scalar_one_or_none()
    style_dict = None
    if sig:
        style_dict = {
            "avg_sentence_length": sig.avg_sentence_length,
            "passive_voice_ratio": sig.passive_voice_ratio,
            "avg_paragraph_length": sig.avg_paragraph_length,
            "vocabulary_sophistication": sig.vocabulary_sophistication,
            "hedging_frequency": sig.hedging_frequency,
            "transition_frequency": sig.transition_frequency,
            "formality_score": sig.formality_score,
            "citation_style_preference": sig.citation_style_preference,
            "argumentation_style": sig.argumentation_style,
            "first_person_usage": sig.first_person_usage,
        }

    # Build orchestrator and execute
    orchestrator = _build_orchestrator()
    task = {
        "task_id": str(uuid.uuid4()),
        "writing_mode": req.writing_mode,
        "user_prompt": req.prompt,
        "user_input_text": req.input_text,
        "user_profile": profile_dict,
        "style_signature": style_dict,
        "project_id": req.project_id,
        "additional_instructions": req.additional_instructions,
        "max_sources": req.max_sources,
        "review_type": req.review_type,
    }
    result = await orchestrator.execute(task)
    payload = result.payload

    # Save session
    session = WritingSession(
        user_id=user.id,
        project_id=uuid.UUID(req.project_id) if req.project_id else None,
        writing_mode=req.writing_mode,
        user_prompt=req.prompt,
        user_input_text=req.input_text,
        additional_instructions=req.additional_instructions,
        generated_output=payload.get("generated_output", ""),
        cited_output=payload.get("cited_output", ""),
        bibliography="\n".join(payload.get("bibliography", [])),
        word_count=payload.get("word_count", 0),
        sources_used=payload.get("sources", []),
        language_level_config=None,
        style_params_used=style_dict,
        integrity_status=payload.get("integrity_status"),
        integrity_report=payload.get("integrity_report"),
        readability_score=payload.get("readability_score"),
        style_match_score=payload.get("style_match_score"),
        model_used=payload.get("model_used"),
        processing_time_ms=payload.get("processing_time_ms"),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "session_id": str(session.id),
        "status": "completed",
        "output": {
            "text": payload.get("cited_output", payload.get("generated_output", "")),
            "word_count": payload.get("word_count", 0),
            "readability_score": payload.get("readability_score"),
            "sources_used": len(payload.get("sources", [])),
            "citation_count": len(payload.get("citation_map", [])),
            "integrity_status": payload.get("integrity_status"),
        },
        "sources": payload.get("sources", [])[:20],
        "evidence_traces": payload.get("evidence_traces", []),
        "bibliography": payload.get("bibliography", []),
        "integrity_report": payload.get("integrity_report", {}),
        "processing_time_ms": payload.get("processing_time_ms"),
    }


@router.get("/{session_id}")
async def get_session(
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
        "writing_mode": session.writing_mode,
        "prompt": session.user_prompt,
        "output": session.cited_output or session.generated_output,
        "bibliography": session.bibliography,
        "integrity_status": session.integrity_status,
        "word_count": session.word_count,
        "user_action": session.user_action,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }


@router.post("/{session_id}/feedback")
async def submit_feedback(
    session_id: str,
    req: FeedbackRequest,
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

    session.user_action = req.signal_type
    if req.edit_diff:
        session.user_edits = req.edit_diff

    signal = FeedbackSignal(
        user_id=user.id,
        session_id=session.id,
        signal_type=req.signal_type,
        edit_diff=req.edit_diff,
        comments=req.comments,
    )
    db.add(signal)
    await db.commit()

    return {"status": "feedback_recorded", "signal_type": req.signal_type}
