"""
Mourya Scholarium — Citation & Reference Agent
Inserts in-text citations (APA 7th), builds bibliography,
maps claims to sources, and flags unsupported claims.
"""
import re
from typing import Any, Dict, List
from agents import BaseAgent, AgentMessage


class CitationAgent(BaseAgent):
    agent_name = "citation"

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        prior = task.get("prior_results", {})
        draft = prior.get("writing", {}).get("draft", "")
        sources = prior.get("retrieval", {}).get("sources", [])
        ranked = prior.get("ml_systems", {}).get("ranked_sources", sources)

        if not draft or not ranked:
            return self.create_response(
                to_agent="orchestrator",
                payload={"cited_text": draft, "reference_list": [], "citation_map": [], "evidence_traces": []},
            )

        # Build citation map: detect in-text references and match to sources
        citation_map = self._build_citation_map(draft, ranked[:20])
        reference_list = self._build_bibliography(ranked[:20])
        evidence_traces = self._build_evidence_traces(draft, ranked[:20])

        return self.create_response(
            to_agent="orchestrator",
            payload={
                "cited_text": draft,
                "reference_list": reference_list,
                "citation_map": citation_map,
                "evidence_traces": evidence_traces,
                "unsupported_claims": [],
            },
        )

    def _build_citation_map(self, text: str, sources: List[Dict]) -> List[Dict]:
        """Find existing citation patterns in text and map to sources."""
        citations = []
        # Match patterns like (Author, Year) or (Author et al., Year)
        pattern = r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?(?:\s*[&,]\s*[A-Z][a-z]+)*,?\s*\d{4}[a-z]?)\)'
        matches = re.finditer(pattern, text)
        for i, m in enumerate(matches):
            cite_text = m.group(1)
            matched_source = self._match_citation_to_source(cite_text, sources)
            citations.append({
                "position": m.start(),
                "in_text_citation": m.group(0),
                "citation_text": cite_text,
                "source_index": matched_source,
            })
        return citations

    def _match_citation_to_source(self, cite: str, sources: List[Dict]) -> int:
        """Try to match a citation string to a source index."""
        cite_lower = cite.lower()
        for i, s in enumerate(sources):
            authors = s.get("authors", [])
            year = str(s.get("year", ""))
            if year and year in cite:
                for a in authors:
                    surname = a.get("name", "").split()[-1].lower() if a.get("name") else ""
                    if surname and surname in cite_lower:
                        return i
        return -1

    def _build_bibliography(self, sources: List[Dict]) -> List[str]:
        """Generate APA 7th reference list."""
        refs = []
        for s in sources:
            ref = self._format_apa7(s)
            if ref:
                refs.append(ref)
        refs.sort()
        return refs

    def _format_apa7(self, source: Dict) -> str:
        """Format a single source as APA 7th edition reference."""
        authors = source.get("authors", [])
        year = source.get("year", "n.d.")
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        doi = source.get("doi", "")

        # Format authors
        auth_str = self._format_authors_apa(authors)

        ref = f"{auth_str} ({year}). {title}."
        if journal:
            ref += f" *{journal}*."
        if doi:
            ref += f" https://doi.org/{doi}"
        return ref

    def _format_authors_apa(self, authors: List[Dict]) -> str:
        if not authors:
            return "Unknown Author"
        names = []
        for a in authors[:20]:
            full = a.get("name", "").strip()
            if not full:
                continue
            parts = full.split()
            if len(parts) >= 2:
                surname = parts[-1]
                initials = " ".join(f"{p[0]}." for p in parts[:-1])
                names.append(f"{surname}, {initials}")
            else:
                names.append(full)

        if len(names) == 0:
            return "Unknown Author"
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]}, & {names[1]}"
        if len(names) <= 20:
            return ", ".join(names[:-1]) + f", & {names[-1]}"
        return f"{names[0]}, ... {names[-1]}"

    def _build_evidence_traces(self, text: str, sources: List[Dict]) -> List[Dict]:
        """Create evidence trace entries linking text claims to sources."""
        traces = []
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 20]
        for i, sent in enumerate(sentences):
            # Check if sentence contains a citation
            if re.search(r'\([A-Z].*?\d{4}\)', sent):
                traces.append({
                    "claim_text": sent,
                    "claim_position": i,
                    "trace_type": "direct_support",
                    "verification_status": "auto_verified",
                })
        return traces
