"""
Mourya Scholarium — Integrity & Safety Agent
Validates claim-source alignment, detects unsupported statements,
blocks fabricated citations, and produces integrity reports.
"""
import re
from typing import Any, Dict, List
from agents import BaseAgent, AgentMessage


class IntegrityAgent(BaseAgent):
    agent_name = "integrity"

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        prior = task.get("prior_results", {})
        draft = prior.get("writing", {}).get("draft", "")
        sources = prior.get("retrieval", {}).get("sources", [])
        citation_map = prior.get("citation", {}).get("citation_map", [])

        report = self._run_checks(draft, sources, citation_map)

        return self.create_response(
            to_agent="orchestrator",
            payload=report,
            confidence=report.get("confidence_score", 1.0),
            warnings=report.get("recommendations", []),
        )

    def _run_checks(self, draft: str, sources: List[Dict], citation_map: List[Dict]) -> Dict:
        hallucination_flags = []
        fabricated_flags = []
        unsupported = []
        overlap_warnings = []

        # 1. Check for citations that don't match any source
        source_authors = set()
        for s in sources:
            for a in s.get("authors", []):
                name = a.get("name", "")
                if name:
                    surname = name.split()[-1].lower()
                    source_authors.add(surname)

        cited_in_text = re.findall(r'\(([A-Z][a-z]+)', draft)
        for cite_author in cited_in_text:
            if cite_author.lower() not in source_authors and cite_author.lower() not in {"e", "i"}:
                fabricated_flags.append({
                    "citation_author": cite_author,
                    "severity": "warning",
                    "message": f"Citation to '{cite_author}' may not match retrieved sources",
                })

        # 2. Check for sentences with factual claims but no citation
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', draft) if len(s.strip()) > 30]
        claim_indicators = [
            r'\d+%', r'significantly', r'found that', r'showed that',
            r'reported', r'demonstrated', r'according to', r'revealed',
            r'increased by', r'decreased by', r'correlation',
        ]
        for sent in sentences:
            has_claim = any(re.search(p, sent, re.I) for p in claim_indicators)
            has_citation = bool(re.search(r'\([A-Z].*?\d{4}\)', sent))
            if has_claim and not has_citation:
                unsupported.append({
                    "claim_text": sent[:200],
                    "severity": "warning",
                    "message": "Factual claim without citation support",
                })

        # 3. Determine overall status
        if len(fabricated_flags) > 3:
            status = "fail"
        elif fabricated_flags or len(unsupported) > 5:
            status = "warning"
        else:
            status = "pass"

        confidence = max(0.0, 1.0 - len(fabricated_flags) * 0.1 - len(unsupported) * 0.05)

        recommendations = []
        if fabricated_flags:
            recommendations.append("Some citations may not match retrieved sources — verify manually.")
        if unsupported:
            recommendations.append(f"{len(unsupported)} claims lack citation support — consider adding references.")

        return {
            "integrity_status": status,
            "hallucination_flags": hallucination_flags,
            "fabricated_citation_flags": fabricated_flags,
            "unsupported_claims": unsupported,
            "overlap_warnings": overlap_warnings,
            "source_legality_issues": [],
            "confidence_score": round(confidence, 2),
            "recommendations": recommendations,
        }
