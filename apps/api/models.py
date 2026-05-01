"""
Mourya Scholarium — SQLAlchemy ORM Models
Complete schema for all entities: users, profiles, style signatures,
projects, writing sessions, sources, evidence traces, citations,
feedback signals, integrity reports, and review sessions.
"""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, TypeDecorator, JSON,
)
from sqlalchemy.orm import relationship
from database import Base
from config import settings


# ─── Portable UUID type (works on SQLite + PostgreSQL) ────
class PortableUUID(TypeDecorator):
    """Platform-independent UUID type. Uses PostgreSQL UUID when available, else CHAR(36)."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return str(value)
        return value


# Use JSON (works everywhere) instead of JSONB_COMPAT (PostgreSQL-only)
JSONB_COMPAT = JSON


def _utcnow() -> datetime:
    """Return current UTC time (timezone-aware). Used as column default."""
    return datetime.now(timezone.utc)


def gen_uuid() -> uuid.UUID:
    return uuid.uuid4()


# ─── Users ───────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    institution = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    style_signature = relationship("StyleSignature", back_populates="user", uselist=False, cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    writing_sessions = relationship("WritingSession", back_populates="user", cascade="all, delete-orphan")
    feedback_signals = relationship("FeedbackSignal", back_populates="user", cascade="all, delete-orphan")


# ─── User Profiles ───────────────────────────────────────

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    english_level = Column(String(50), nullable=False)          # beginner | intermediate | advanced | publication_ready
    academic_level = Column(String(50), nullable=False)         # undergraduate | postgraduate | phd | professional | faculty
    discipline = Column(String(255), nullable=True)
    sub_field = Column(String(255), nullable=True)
    topic = Column(Text, nullable=True)
    citation_style = Column(String(50), default="APA7")
    academic_only_sources = Column(Boolean, default=True)
    target_output_level = Column(String(50), default="match_current")  # match_current | elevate_slightly | publication_ready

    preferred_complexity = Column(String(50), nullable=True)
    writing_type_needed = Column(String(100), nullable=True)
    writing_style = Column(String(100), nullable=True)
    tone_preference = Column(String(50), default="formal_but_accessible")
    orientation = Column(String(50), nullable=True)             # thesis | journal | report

    preservation_priorities = Column(JSONB_COMPAT, default=list)       # ["vocabulary", "sentence_length", ...]
    improvement_targets = Column(JSONB_COMPAT, default=list)           # ["grammar", "coherence", ...]

    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="profile")


# ─── Style Signatures ───────────────────────────────────

class StyleSignature(Base):
    __tablename__ = "style_signatures"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    avg_sentence_length = Column(Float, nullable=True)
    sentence_length_variance = Column(Float, nullable=True)
    passive_voice_ratio = Column(Float, nullable=True)
    avg_paragraph_length = Column(Float, nullable=True)
    vocabulary_sophistication = Column(Float, nullable=True)
    hedging_frequency = Column(Float, nullable=True)
    transition_frequency = Column(Float, nullable=True)
    formality_score = Column(Float, nullable=True)
    citation_style_preference = Column(String(50), nullable=True)  # parenthetical | narrative
    argumentation_style = Column(String(50), nullable=True)        # deductive | inductive
    first_person_usage = Column(Float, nullable=True)

    sample_text_hash = Column(String(64), nullable=True)   # SHA-256 of sample (for change detection, never stored raw)
    sample_word_count = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="style_signature")


# ─── Projects ────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    discipline = Column(String(255), nullable=True)
    topic = Column(Text, nullable=True)
    project_type = Column(String(100), nullable=True)   # thesis | journal_paper | review | proposal
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="projects")
    writing_sessions = relationship("WritingSession", back_populates="project", cascade="all, delete-orphan")
    review_sessions = relationship("ReviewSession", back_populates="project", cascade="all, delete-orphan")


# ─── Writing Sessions ────────────────────────────────────

class WritingSession(Base):
    __tablename__ = "writing_sessions"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    project_id = Column(PortableUUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    writing_mode = Column(String(100), nullable=False)       # write_from_prompt | rewrite | literature_review | ...
    user_prompt = Column(Text, nullable=False)
    user_input_text = Column(Text, nullable=True)            # For rewrite mode
    additional_instructions = Column(Text, nullable=True)

    generated_output = Column(Text, nullable=True)
    cited_output = Column(Text, nullable=True)
    bibliography = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)

    sources_used = Column(JSONB_COMPAT, default=list)               # List of source IDs
    language_level_config = Column(JSONB_COMPAT, nullable=True)
    style_params_used = Column(JSONB_COMPAT, nullable=True)

    integrity_status = Column(String(50), nullable=True)     # pass | warning | fail
    integrity_report = Column(JSONB_COMPAT, nullable=True)

    user_action = Column(String(50), default="pending")      # pending | accepted | edited | rejected
    user_edits = Column(Text, nullable=True)

    readability_score = Column(Float, nullable=True)
    style_match_score = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    token_count_input = Column(Integer, nullable=True)
    token_count_output = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="writing_sessions")
    project = relationship("Project", back_populates="writing_sessions")
    evidence_traces = relationship("EvidenceTrace", back_populates="session", cascade="all, delete-orphan")
    citation_entries = relationship("CitationEntry", back_populates="session", cascade="all, delete-orphan")
    feedback_signals = relationship("FeedbackSignal", back_populates="session", cascade="all, delete-orphan")


# ─── Sources (Cached Scholarly Metadata) ─────────────────

class Source(Base):
    __tablename__ = "sources"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    doi = Column(String(255), unique=True, nullable=True, index=True)
    title = Column(Text, nullable=False)
    authors = Column(JSONB_COMPAT, default=list)                    # [{name, affiliation, orcid}]
    year = Column(Integer, nullable=True)
    journal = Column(String(500), nullable=True)
    publisher = Column(String(500), nullable=True)
    volume = Column(String(50), nullable=True)
    issue = Column(String(50), nullable=True)
    pages = Column(String(100), nullable=True)
    url = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)

    source_type = Column(String(100), nullable=True)         # journal_article | conference_paper | book_chapter | ...
    is_peer_reviewed = Column(Boolean, nullable=True)
    is_open_access = Column(Boolean, nullable=True)
    citation_count = Column(Integer, nullable=True)
    influential_citation_count = Column(Integer, nullable=True)
    fields_of_study = Column(JSONB_COMPAT, default=list)

    trust_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    retraction_status = Column(String(50), default="none")
    database_source = Column(String(100), nullable=True)     # semantic_scholar | crossref | openalex | core
    embedding_id = Column(String(255), nullable=True)        # Reference to vector DB

    retrieved_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


# ─── Evidence Traces ─────────────────────────────────────

class EvidenceTrace(Base):
    __tablename__ = "evidence_traces"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    session_id = Column(PortableUUID(), ForeignKey("writing_sessions.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(PortableUUID(), ForeignKey("sources.id"), nullable=True)

    claim_text = Column(Text, nullable=False)
    claim_position = Column(Integer, nullable=True)
    supporting_text = Column(Text, nullable=True)
    match_confidence = Column(Float, nullable=True)
    trace_type = Column(String(50), default="direct_support")   # direct_support | indirect | background
    verification_status = Column(String(50), default="auto_verified")

    created_at = Column(DateTime, default=_utcnow)

    session = relationship("WritingSession", back_populates="evidence_traces")
    source = relationship("Source")


# ─── Citation Entries ─────────────────────────────────────

class CitationEntry(Base):
    __tablename__ = "citation_entries"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    session_id = Column(PortableUUID(), ForeignKey("writing_sessions.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(PortableUUID(), ForeignKey("sources.id"), nullable=True)

    in_text_citation = Column(Text, nullable=True)
    reference_entry = Column(Text, nullable=True)
    citation_style = Column(String(50), default="APA7")
    position_in_text = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=_utcnow)

    session = relationship("WritingSession", back_populates="citation_entries")
    source = relationship("Source")


# ─── Feedback Signals ─────────────────────────────────────

class FeedbackSignal(Base):
    __tablename__ = "feedback_signals"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(PortableUUID(), ForeignKey("writing_sessions.id", ondelete="CASCADE"), nullable=False)

    signal_type = Column(String(50), nullable=False)         # accept | edit | reject
    edit_diff = Column(Text, nullable=True)
    feature_deltas = Column(JSONB_COMPAT, nullable=True)
    comments = Column(Text, nullable=True)

    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="feedback_signals")
    session = relationship("WritingSession", back_populates="feedback_signals")


# ─── Integrity Reports ───────────────────────────────────

class IntegrityReport(Base):
    __tablename__ = "integrity_reports"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    session_id = Column(PortableUUID(), ForeignKey("writing_sessions.id", ondelete="CASCADE"), nullable=False)

    integrity_status = Column(String(50), nullable=False)    # pass | warning | fail
    hallucination_flags = Column(JSONB_COMPAT, default=list)
    fabricated_citation_flags = Column(JSONB_COMPAT, default=list)
    unsupported_claims = Column(JSONB_COMPAT, default=list)
    overlap_warnings = Column(JSONB_COMPAT, default=list)
    source_legality_issues = Column(JSONB_COMPAT, default=list)
    confidence_score = Column(Float, nullable=True)
    recommendations = Column(JSONB_COMPAT, default=list)

    created_at = Column(DateTime, default=_utcnow)


# ─── Review Sessions ─────────────────────────────────────

class ReviewSession(Base):
    __tablename__ = "review_sessions"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    project_id = Column(PortableUUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(PortableUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    review_type = Column(String(50), nullable=False)         # narrative | systematic | scoping | critical | integrative
    topic = Column(Text, nullable=False)
    scope = Column(Text, nullable=True)
    inclusion_criteria = Column(JSONB_COMPAT, default=list)
    exclusion_criteria = Column(JSONB_COMPAT, default=list)

    search_strategy = Column(Text, nullable=True)
    sources_found = Column(Integer, nullable=True)
    sources_included = Column(Integer, nullable=True)

    themes = Column(JSONB_COMPAT, default=list)
    evidence_table = Column(JSONB_COMPAT, default=list)
    gap_analysis = Column(Text, nullable=True)
    synthesized_output = Column(Text, nullable=True)

    status = Column(String(50), default="in_progress")       # in_progress | completed | failed
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    project = relationship("Project", back_populates="review_sessions")


# ─── Evaluation Logs ─────────────────────────────────────

class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"

    id = Column(PortableUUID(), primary_key=True, default=gen_uuid)
    session_id = Column(PortableUUID(), ForeignKey("writing_sessions.id", ondelete="CASCADE"), nullable=True)

    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=True)
    metric_metadata = Column(JSONB_COMPAT, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
