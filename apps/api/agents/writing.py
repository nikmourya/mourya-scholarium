"""
Mourya Scholarium — Writing Engine Agent
Generates academic text using Claude-class LLM with source package,
style parameters, and language level config.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import anthropic  # type: ignore[import-untyped]
from agents import BaseAgent, AgentMessage
from agents.prompt_engineering import PromptStore
from config import settings


class WritingAgent(BaseAgent):
    agent_name = "writing"

    def __init__(self) -> None:
        super().__init__()
        self.client: Optional[anthropic.AsyncAnthropic] = None
        if settings.anthropic_api_key:
            self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        prior = task.get("prior_results", {})
        writing_mode = task.get("writing_mode", "write_from_prompt")
        user_prompt = task.get("user_prompt", "")
        user_input_text = task.get("user_input_text", "")

        # Gather context from prior agents
        lang_config = prior.get("pedagogy", {}).get("language_level_config", {})
        style_params = prior.get("style_learning", {}).get("style_params", {})
        sources = prior.get("retrieval", {}).get("sources", [])
        ranked_sources = prior.get("ml_systems", {}).get("ranked_sources", sources)
        review_structure = prior.get("literature_review", {}).get("review_structure", {})

        # Select model based on complexity
        model = self._select_model(writing_mode)

        # Build the system prompt
        system_prompt = PromptStore.get_writing_prompt(writing_mode, lang_config, style_params)

        # Build user message with sources
        user_msg = self._build_user_message(
            writing_mode, user_prompt, user_input_text,
            ranked_sources[:20], review_structure,
            task.get("additional_instructions"),
        )

        # Generate via LLM
        draft = ""
        if self.client:
            try:
                response = await self.client.messages.create(
                    model=model,
                    max_tokens=8000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_msg}],
                )
                draft = response.content[0].text
            except Exception as e:
                self.logger.error(f"LLM generation failed: {e}")
                draft = f"[Generation error: {e}. Please check your API key and try again.]"
        else:
            draft = self._mock_generation(writing_mode, user_prompt, ranked_sources)

        word_count = len(draft.split())

        return self.create_response(
            to_agent="orchestrator",
            payload={
                "draft": draft,
                "word_count": word_count,
                "model_used": model,
                "readability_score": None,  # Computed in post-processing
                "style_match_score": None,
            },
        )

    def _select_model(self, mode: str) -> str:
        if mode in ("literature_review",):
            return settings.anthropic_model_opus
        return settings.anthropic_model_sonnet

    def _build_user_message(
        self,
        mode: str,
        prompt: str,
        input_text: str,
        sources: List[Dict[str, Any]],
        review: Any,
        extra: Optional[str],
    ) -> str:
        parts: List[str] = []
        if mode == "rewrite" and input_text:
            parts.append(f"TEXT TO REWRITE:\n{input_text}\n")
            parts.append(f"INSTRUCTIONS: {prompt}\n")
        else:
            parts.append(f"WRITING REQUEST: {prompt}\n")

        if extra:
            parts.append(f"ADDITIONAL INSTRUCTIONS: {extra}\n")

        if review:
            parts.append(f"REVIEW STRUCTURE:\n{self._format_review(review)}\n")

        if sources:
            parts.append("AVAILABLE SCHOLARLY SOURCES (use these for citations):\n")
            for i, s in enumerate(sources[:20], 1):
                auth = self._format_authors_short(s.get("authors", []))
                year = s.get("year", "n.d.")
                parts.append(f"[{i}] {auth} ({year}). {s.get('title', '')}")
                if s.get("journal"):
                    parts.append(f"    Journal: {s['journal']}")
                if s.get("doi"):
                    parts.append(f"    DOI: {s['doi']}")
                if s.get("abstract"):
                    parts.append(f"    Abstract: {s['abstract'][:300]}")
                parts.append("")

        return "\n".join(parts)

    def _format_authors_short(self, authors: List[Dict[str, Any]]) -> str:
        if not authors:
            return "Unknown"
        names = [a.get("name", "") for a in authors[:3]]
        if len(authors) > 3:
            return f"{names[0]} et al."
        return ", ".join(names)

    def _format_review(self, review: Any) -> str:
        if isinstance(review, dict):
            themes = review.get("themes", [])
            parts: List[str] = []
            for t in themes:
                parts.append(f"- Theme: {t.get('theme_name', 'Untitled')}")
                parts.append(f"  Sources: {len(t.get('sources', []))}")
            return "\n".join(parts)
        return str(review)

    def _mock_generation(self, mode: str, prompt: str, sources: List[Dict[str, Any]]) -> str:
        """Produce a placeholder draft when no LLM API key is configured."""
        src_refs = ""
        for _i, s in enumerate(sources[:5], 1):
            auth = self._format_authors_short(s.get("authors", []))
            year = s.get("year", "n.d.")
            src_refs += f"({auth}, {year}), "

        return (
            f"[DEMO OUTPUT — Configure ANTHROPIC_API_KEY for real generation]\n\n"
            f"## Academic Draft\n\n"
            f"Topic: {prompt[:200]}\n\n"
            f"This section provides a synthesized overview of the research landscape. "
            f"Several studies have examined this topic {src_refs.rstrip(', ')}. "
            f"The literature suggests that further investigation is needed to address "
            f"existing gaps in the current body of knowledge.\n\n"
            f"Mode: {mode} | Sources available: {len(sources)}"
        )
