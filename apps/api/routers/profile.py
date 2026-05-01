"""
Mourya Scholarium — Profile Router
POST /api/v1/profile          — create/update user profile
POST /api/v1/profile/style-sample  — upload writing sample
GET  /api/v1/profile/style-signature — get computed style signature
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, UserProfile, StyleSignature
from dependencies import get_current_user
from agents.style_learning import StyleLearningAgent

router = APIRouter()
style_agent = StyleLearningAgent()


class ProfileRequest(BaseModel):
    english_level: str
    academic_level: str
    discipline: Optional[str] = None
    sub_field: Optional[str] = None
    topic: Optional[str] = None
    citation_style: str = "APA7"
    academic_only_sources: bool = True
    target_output_level: str = "match_current"
    preferred_complexity: Optional[str] = None
    writing_type_needed: Optional[str] = None
    writing_style: Optional[str] = None
    tone_preference: str = "formal_but_accessible"
    orientation: Optional[str] = None
    preservation_priorities: List[str] = []
    improvement_targets: List[str] = []


class StyleSampleRequest(BaseModel):
    sample_text: str  # 100-500+ words


@router.post("")
async def create_or_update_profile(
    req: ProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    if profile:
        for key, val in req.model_dump(exclude_unset=True).items():
            setattr(profile, key, val)
    else:
        profile = UserProfile(user_id=user.id, **req.model_dump())
        db.add(profile)

    await db.commit()
    await db.refresh(profile)
    return {"status": "ok", "profile_id": str(profile.id)}


@router.post("/style-sample")
async def upload_style_sample(
    req: StyleSampleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if len(req.sample_text.split()) < 20:
        raise HTTPException(400, "Sample must be at least 20 words")

    features = style_agent.analyze_sample(req.sample_text)

    result = await db.execute(select(StyleSignature).where(StyleSignature.user_id == user.id))
    sig = result.scalar_one_or_none()

    if sig:
        for key, val in features.items():
            if hasattr(sig, key):
                setattr(sig, key, val)
    else:
        sig = StyleSignature(user_id=user.id, **{k: v for k, v in features.items() if k != "sample_text_hash" or True})
        db.add(sig)

    await db.commit()
    await db.refresh(sig)
    return {"status": "ok", "style_signature_id": str(sig.id), "features": features}


@router.get("/style-signature")
async def get_style_signature(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StyleSignature).where(StyleSignature.user_id == user.id))
    sig = result.scalar_one_or_none()
    if not sig:
        return {"style_signature": None, "message": "No style sample uploaded yet"}

    return {
        "style_signature": {
            "avg_sentence_length": sig.avg_sentence_length,
            "sentence_length_variance": sig.sentence_length_variance,
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
    }
