"""
Mourya Scholarium — Academic Retrieval Agent
Discovers scholarly sources from Semantic Scholar, CrossRef, OpenAlex.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List
import httpx
from agents import BaseAgent, AgentMessage
from config import settings


class RetrievalAgent(BaseAgent):
    agent_name = "retrieval"

    SS_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    CR_URL = "https://api.crossref.org/works"
    OA_URL = "https://api.openalex.org/works"

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        query = task.get("user_prompt", "")[:200]
        max_src = task.get("max_sources", 20)
        disc = task.get("user_profile", {}).get("discipline", "")
        if disc:
            query = f"{query} {disc}"

        all_sources: List[Dict[str, Any]] = []
        results = await asyncio.gather(
            self._search_ss(query, max_src),
            self._search_cr(query, max_src),
            self._search_oa(query, max_src),
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, list):
                all_sources.extend(r)

        deduped = self._deduplicate(all_sources)
        filtered = [s for s in deduped if self._is_academic(s)][:max_src * 2]

        return self.create_response(
            to_agent="orchestrator",
            payload={"sources": filtered, "total_found": len(all_sources), "after_dedup": len(deduped)},
        )

    async def _search_ss(self, query: str, limit: int) -> List[Dict[str, Any]]:
        headers: Dict[str, str] = {}
        if settings.semantic_scholar_api_key:
            headers["x-api-key"] = settings.semantic_scholar_api_key
        params = {"query": query, "limit": min(limit, 50),
                  "fields": "title,authors,year,abstract,doi,url,venue,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy,publicationTypes"}
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(self.SS_URL, params=params, headers=headers)
            if r.status_code != 200:
                return []
            return [self._norm_ss(p) for p in r.json().get("data", []) if p.get("title")]

    async def _search_cr(self, query: str, limit: int) -> List[Dict[str, Any]]:
        headers: Dict[str, str] = {}
        if settings.crossref_mailto:
            headers["User-Agent"] = f"MouryaScholarium/1.0 (mailto:{settings.crossref_mailto})"
        params = {"query": query, "rows": min(limit, 50)}
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(self.CR_URL, params=params, headers=headers)
            if r.status_code != 200:
                return []
            return [self._norm_cr(i) for i in r.json().get("message", {}).get("items", []) if i.get("title")]

    async def _search_oa(self, query: str, limit: int) -> List[Dict[str, Any]]:
        params = {"search": query, "per_page": min(limit, 50), "mailto": settings.openalex_mailto or "ms@scholarium.app"}
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(self.OA_URL, params=params)
            if r.status_code != 200:
                return []
            return [self._norm_oa(i) for i in r.json().get("results", []) if i.get("title")]

    def _norm_ss(self, p: Dict[str, Any]) -> Dict[str, Any]:
        authors = [{"name": a.get("name", "")} for a in (p.get("authors") or [])]
        return {"title": p.get("title", ""), "authors": authors, "year": p.get("year"),
                "journal": p.get("venue", ""), "doi": p.get("doi"), "url": p.get("url", ""),
                "abstract": (p.get("abstract") or "")[:2000], "source_type": "journal_article",
                "is_peer_reviewed": True, "is_open_access": p.get("isOpenAccess", False),
                "citation_count": p.get("citationCount", 0),
                "influential_citation_count": p.get("influentialCitationCount", 0),
                "fields_of_study": p.get("fieldsOfStudy") or [], "database_source": "semantic_scholar"}

    def _norm_cr(self, i: Dict[str, Any]) -> Dict[str, Any]:
        title = i.get("title", [""])[0] if isinstance(i.get("title"), list) else str(i.get("title", ""))
        authors = [{"name": f"{a.get('given', '')} {a.get('family', '')}".strip()} for a in (i.get("author") or [])]
        year = None
        dp = i.get("published-print", {}).get("date-parts", [[None]])
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
        journal = (i.get("container-title") or [""])[0] if isinstance(i.get("container-title"), list) else ""
        return {"title": title, "authors": authors, "year": year, "journal": journal,
                "doi": i.get("DOI"), "url": f"https://doi.org/{i.get('DOI', '')}" if i.get("DOI") else "",
                "abstract": (i.get("abstract") or "")[:2000], "source_type": "journal_article",
                "is_peer_reviewed": True, "is_open_access": False,
                "citation_count": i.get("is-referenced-by-count", 0),
                "influential_citation_count": 0, "fields_of_study": [], "database_source": "crossref"}

    def _norm_oa(self, i: Dict[str, Any]) -> Dict[str, Any]:
        authors = [{"name": a.get("author", {}).get("display_name", "")} for a in (i.get("authorships") or [])]
        loc = i.get("primary_location") or {}
        journal = (loc.get("source") or {}).get("display_name", "")
        doi_raw = i.get("doi", "") or ""
        doi = doi_raw.replace("https://doi.org/", "") if doi_raw else None
        return {"title": i.get("title", ""), "authors": authors, "year": i.get("publication_year"),
                "journal": journal, "doi": doi, "url": doi_raw, "abstract": "",
                "source_type": "journal_article", "is_peer_reviewed": True,
                "is_open_access": i.get("open_access", {}).get("is_oa", False),
                "citation_count": i.get("cited_by_count", 0), "influential_citation_count": 0,
                "fields_of_study": [c.get("display_name", "") for c in (i.get("concepts") or [])[:5]],
                "database_source": "openalex"}

    def _deduplicate(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_dois: set[str] = set()
        seen_titles: set[str] = set()
        unique: List[Dict[str, Any]] = []
        for s in sources:
            doi = (s.get("doi") or "").strip().lower()
            tk = (s.get("title") or "").strip().lower()[:100]
            if doi and doi in seen_dois:
                continue
            if tk and tk in seen_titles:
                continue
            if doi:
                seen_dois.add(doi)
            if tk:
                seen_titles.add(tk)
            unique.append(s)
        return unique

    def _is_academic(self, s: Dict[str, Any]) -> bool:
        return len(s.get("title", "")) >= 10
