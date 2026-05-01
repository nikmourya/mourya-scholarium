"""
Mourya Scholarium — Literature Review Agent
Handles narrative review workflow: theme extraction, synthesis structure, gap analysis.
"""
from typing import Any, Dict, List
from agents import BaseAgent, AgentMessage


class LiteratureReviewAgent(BaseAgent):
    agent_name = "literature_review"

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        prior = task.get("prior_results", {})
        sources = prior.get("ml_systems", {}).get("ranked_sources", [])
        if not sources:
            sources = prior.get("retrieval", {}).get("sources", [])

        review_type = task.get("review_type", "narrative")
        topic = task.get("user_prompt", "")

        if review_type == "narrative":
            structure = self._build_narrative_structure(sources, topic)
        else:
            structure = self._build_narrative_structure(sources, topic)

        return self.create_response(
            to_agent="orchestrator",
            payload={"review_structure": structure, "review_type": review_type},
        )

    def _build_narrative_structure(self, sources: List[Dict], topic: str) -> Dict:
        """Create a thematic structure for a narrative literature review."""
        # Cluster sources into themes based on fields_of_study and keywords
        themes = self._extract_themes(sources)
        gap_analysis = self._identify_gaps(sources, themes)

        return {
            "review_type": "narrative",
            "topic": topic,
            "total_sources": len(sources),
            "themes": themes,
            "gap_analysis": gap_analysis,
            "suggested_structure": [
                "Introduction and scope",
                *[t["theme_name"] for t in themes],
                "Research gaps and future directions",
                "Conclusion",
            ],
        }

    def _extract_themes(self, sources: List[Dict]) -> List[Dict]:
        """Group sources into thematic clusters using field/keyword overlap."""
        if not sources:
            return [{"theme_name": "General Overview", "sources": [], "source_count": 0}]

        # Collect all fields
        field_counts = {}
        for s in sources:
            for f in s.get("fields_of_study", []):
                f_clean = f.strip()
                if f_clean:
                    field_counts[f_clean] = field_counts.get(f_clean, 0) + 1

        # Pick top fields as themes (max 6)
        sorted_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
        top_fields = [f for f, c in sorted_fields[:6] if c >= 1]

        if not top_fields:
            # Fallback: group by decade
            return self._group_by_decade(sources)

        themes = []
        assigned = set()
        for field in top_fields:
            theme_sources = []
            for i, s in enumerate(sources):
                if i in assigned:
                    continue
                if field.lower() in [f.lower() for f in s.get("fields_of_study", [])]:
                    theme_sources.append(i)
                    assigned.add(i)
            if theme_sources:
                themes.append({
                    "theme_name": field,
                    "sources": theme_sources,
                    "source_count": len(theme_sources),
                })

        # Add remaining sources to "Other Studies"
        remaining = [i for i in range(len(sources)) if i not in assigned]
        if remaining:
            themes.append({
                "theme_name": "Additional Studies",
                "sources": remaining,
                "source_count": len(remaining),
            })

        return themes

    def _group_by_decade(self, sources: List[Dict]) -> List[Dict]:
        decades = {}
        for i, s in enumerate(sources):
            year = s.get("year") or 2020
            decade = (year // 10) * 10
            key = f"{decade}s"
            if key not in decades:
                decades[key] = []
            decades[key].append(i)

        return [{"theme_name": k, "sources": v, "source_count": len(v)}
                for k, v in sorted(decades.items())]

    def _identify_gaps(self, sources: List[Dict], themes: List[Dict]) -> str:
        """Generate a gap analysis statement."""
        gaps = []
        years = [s.get("year", 2020) for s in sources if s.get("year")]
        if years:
            if max(years) < 2024:
                gaps.append("Limited recent studies (post-2024) were identified.")
            if min(years) > 2015:
                gaps.append("Historical context from earlier studies may be underrepresented.")

        small_themes = [t for t in themes if t["source_count"] <= 2]
        if small_themes:
            names = ", ".join(t["theme_name"] for t in small_themes[:3])
            gaps.append(f"Limited coverage found for: {names}.")

        if len(sources) < 10:
            gaps.append("The overall number of sources is limited; broader searches may be warranted.")

        return " ".join(gaps) if gaps else "No significant gaps identified in the retrieved literature."
