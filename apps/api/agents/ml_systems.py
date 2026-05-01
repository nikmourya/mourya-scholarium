"""
Mourya Scholarium — ML Systems Agent
Ranking, source-quality scoring, duplicate detection, and
feedback-aware personalization using XGBoost-style models.
"""
import math
from typing import Any, Dict, List
from agents import BaseAgent, AgentMessage

# In production, these would be trained XGBoost/LightGBM models loaded from disk.
# For MVP, we use a feature-weighted heuristic that mirrors the intended model.


class MLSystemsAgent(BaseAgent):
    agent_name = "ml_systems"

    # Feature weights (mirroring XGBoost feature importances)
    RELEVANCE_WEIGHTS = {
        "citation_count_log": 0.20,
        "is_peer_reviewed": 0.20,
        "has_doi": 0.15,
        "recency": 0.15,
        "is_open_access": 0.05,
        "has_abstract": 0.10,
        "field_match": 0.10,
        "title_length": 0.05,
    }

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        prior = task.get("prior_results", {})
        sources = prior.get("retrieval", {}).get("sources", [])
        discipline = task.get("user_profile", {}).get("discipline", "")

        if not sources:
            return self.create_response(to_agent="orchestrator", payload={"ranked_sources": []})

        scored = [self._score_source(s, discipline) for s in sources]
        scored.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        max_sources = task.get("max_sources", 20)
        ranked = scored[:max_sources]

        return self.create_response(
            to_agent="orchestrator",
            payload={"ranked_sources": ranked, "total_scored": len(scored)},
        )

    def _score_source(self, source: Dict, discipline: str) -> Dict:
        """Compute relevance and trust scores using weighted features."""
        features = self._extract_features(source, discipline)

        # Relevance score (weighted sum)
        relevance = sum(features.get(k, 0) * w for k, w in self.RELEVANCE_WEIGHTS.items())
        relevance = min(1.0, max(0.0, relevance))

        # Trust score
        trust = self._compute_trust(source)

        result = {**source}
        result["relevance_score"] = round(relevance, 3)
        result["trust_score"] = round(trust, 3)
        return result

    def _extract_features(self, source: Dict, discipline: str) -> Dict:
        cc = source.get("citation_count", 0)
        year = source.get("year") or 2020
        current_year = 2026

        features = {
            "citation_count_log": min(1.0, math.log1p(cc) / 8.0),
            "is_peer_reviewed": 1.0 if source.get("is_peer_reviewed") else 0.0,
            "has_doi": 1.0 if source.get("doi") else 0.0,
            "recency": max(0.0, 1.0 - (current_year - year) / 30.0),
            "is_open_access": 1.0 if source.get("is_open_access") else 0.0,
            "has_abstract": 1.0 if source.get("abstract") else 0.0,
            "title_length": min(1.0, len(source.get("title", "")) / 100),
        }

        # Field match
        fields = [f.lower() for f in source.get("fields_of_study", [])]
        disc_lower = discipline.lower() if discipline else ""
        features["field_match"] = 1.0 if any(disc_lower in f or f in disc_lower for f in fields) else 0.3

        return features

    def _compute_trust(self, source: Dict) -> float:
        score = 0.0
        score += 0.30 if source.get("is_peer_reviewed") else 0.0
        score += 0.15 if source.get("doi") else 0.0
        score += 0.15 if source.get("journal") else 0.0
        cc = source.get("citation_count", 0)
        score += min(0.10, math.log1p(cc) / 80.0)
        score += 0.10  # Publisher reputation (default for now)
        year = source.get("year") or 2020
        score += max(0.0, min(0.05, (2026 - year) / 50.0))
        score += 0.10 if source.get("retraction_status", "none") == "none" else 0.0
        score += 0.05 if source.get("is_open_access") else 0.0
        return min(1.0, score)
