"""
Mourya Scholarium — Evaluation Agent
Benchmark hooks, metrics logging, quality checks for citation accuracy,
hallucination rate, readability, style consistency, and feedback signals.
"""
from typing import Any, Dict
from agents import BaseAgent, AgentMessage


class EvaluationAgent(BaseAgent):
    agent_name = "evaluation"

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        prior = task.get("prior_results", {})
        writing = prior.get("writing", {})
        integrity = prior.get("integrity", {})
        citation = prior.get("citation", {})

        metrics = self._compute_metrics(writing, integrity, citation)

        return self.create_response(
            to_agent="orchestrator",
            payload={"metrics": metrics},
        )

    def _compute_metrics(self, writing: Dict, integrity: Dict, citation: Dict) -> Dict:
        draft = writing.get("draft", "")
        word_count = writing.get("word_count", 0)

        # Citation accuracy
        total_citations = len(citation.get("citation_map", []))
        fabricated = len(integrity.get("fabricated_citation_flags", []))
        citation_accuracy = (total_citations - fabricated) / max(total_citations, 1)

        # Hallucination rate
        unsupported = len(integrity.get("unsupported_claims", []))
        sentences = max(1, len([s for s in draft.split('.') if len(s.strip()) > 10]))
        hallucination_rate = unsupported / sentences

        # Readability (simplified — use textstat in production)
        avg_word_len = sum(len(w) for w in draft.split()) / max(len(draft.split()), 1)

        return {
            "citation_count": total_citations,
            "citation_accuracy": round(citation_accuracy, 3),
            "hallucination_rate": round(hallucination_rate, 4),
            "unsupported_claim_count": unsupported,
            "word_count": word_count,
            "avg_word_length": round(avg_word_len, 1),
            "integrity_status": integrity.get("integrity_status", "unknown"),
            "confidence_score": integrity.get("confidence_score", 0),
            "sources_used": len(citation.get("reference_list", [])),
        }


class ProductArchitectAgent(BaseAgent):
    """Planning/config layer for feature gating and workflow rules."""
    agent_name = "product_architect"

    # Feature flags for MVP gating
    FEATURES = {
        "write_from_prompt": True,
        "rewrite": True,
        "literature_review": True,
        "introduction": True,
        "write_from_outline": False,
        "write_from_bullets": False,
        "methodology": False,
        "results_to_prose": False,
        "abstract": False,
        "research_proposal": False,
        "annotated_bibliography": False,
        "systematic_review": False,
        "scoping_review": False,
    }

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        return self.create_response(
            to_agent="orchestrator",
            payload={"features": self.FEATURES, "version": "1.0.0-mvp"},
        )

    @classmethod
    def is_enabled(cls, feature: str) -> bool:
        return cls.FEATURES.get(feature, False)
