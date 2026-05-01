"""
Mourya Scholarium — Lead Orchestrator Agent
Decomposes user requests, selects agents, manages execution order,
reconciles outputs, and enforces quality gates.
"""
import time
from typing import Any, Dict, List, Optional
from agents import BaseAgent, AgentMessage


class OrchestratorAgent(BaseAgent):
    agent_name = "orchestrator"

    def __init__(self, agents: Dict[str, BaseAgent]):
        super().__init__()
        self.agents = agents

    # ── Request classification ──
    WRITING_MODES = {
        "write_from_prompt": {
            "required": ["pedagogy", "style_learning", "retrieval", "ml_systems", "writing", "citation", "integrity", "evaluation"],
            "phases": [
                {"parallel": ["pedagogy", "style_learning"]},
                {"parallel": ["retrieval"]},
                {"sequential": ["ml_systems"]},
                {"sequential": ["writing"]},
                {"sequential": ["citation"]},
                {"sequential": ["integrity"]},
                {"sequential": ["evaluation"]},
            ],
        },
        "rewrite": {
            "required": ["pedagogy", "style_learning", "writing", "integrity", "evaluation"],
            "phases": [
                {"parallel": ["pedagogy", "style_learning"]},
                {"sequential": ["writing"]},
                {"sequential": ["integrity"]},
                {"sequential": ["evaluation"]},
            ],
        },
        "literature_review": {
            "required": ["pedagogy", "style_learning", "retrieval", "ml_systems", "literature_review", "writing", "citation", "integrity", "evaluation"],
            "phases": [
                {"parallel": ["pedagogy", "style_learning"]},
                {"parallel": ["retrieval"]},
                {"sequential": ["ml_systems"]},
                {"sequential": ["literature_review"]},
                {"sequential": ["writing"]},
                {"sequential": ["citation"]},
                {"sequential": ["integrity"]},
                {"sequential": ["evaluation"]},
            ],
        },
        "introduction": {
            "required": ["pedagogy", "style_learning", "retrieval", "ml_systems", "writing", "citation", "integrity", "evaluation"],
            "phases": [
                {"parallel": ["pedagogy", "style_learning"]},
                {"parallel": ["retrieval"]},
                {"sequential": ["ml_systems"]},
                {"sequential": ["writing"]},
                {"sequential": ["citation"]},
                {"sequential": ["integrity"]},
                {"sequential": ["evaluation"]},
            ],
        },
    }

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        """
        Main orchestration entry point.
        task must contain: writing_mode, user_prompt, user_profile, style_signature
        """
        start = time.time()
        writing_mode = task.get("writing_mode", "write_from_prompt")
        mode_config = self.WRITING_MODES.get(writing_mode, self.WRITING_MODES["write_from_prompt"])

        self.logger.info(f"Orchestrating mode={writing_mode}, agents={mode_config['required']}")

        # Build execution context shared across agents
        context: Dict[str, Any] = {
            "user_prompt": task.get("user_prompt", ""),
            "user_input_text": task.get("user_input_text"),
            "user_profile": task.get("user_profile", {}),
            "style_signature": task.get("style_signature"),
            "project_id": task.get("project_id"),
            "writing_mode": writing_mode,
            "additional_instructions": task.get("additional_instructions"),
            "max_sources": task.get("max_sources", 20),
            "review_type": task.get("review_type", "narrative"),
        }

        results: Dict[str, AgentMessage] = {}
        warnings: List[str] = []

        # Execute phases sequentially; within each phase, run agents
        for phase in mode_config["phases"]:
            if "parallel" in phase:
                for agent_key in phase["parallel"]:
                    if agent_key in self.agents:
                        result = await self._run_agent(agent_key, context, results)
                        results[agent_key] = result
                        if result.warnings:
                            warnings.extend(result.warnings)
            elif "sequential" in phase:
                for agent_key in phase["sequential"]:
                    if agent_key in self.agents:
                        result = await self._run_agent(agent_key, context, results)
                        results[agent_key] = result
                        if result.warnings:
                            warnings.extend(result.warnings)

        # Assemble final output
        elapsed = int((time.time() - start) * 1000)
        final = self._assemble_output(results, elapsed)
        final["warnings"] = warnings

        return self.create_response(
            to_agent="ux",
            payload=final,
            task_id=task.get("task_id", ""),
            confidence=results.get("integrity", AgentMessage("", "", "", {})).confidence,
            warnings=warnings,
        )

    async def _run_agent(
        self, agent_key: str, context: Dict[str, Any], prior_results: Dict[str, AgentMessage]
    ) -> AgentMessage:
        """Run a single agent, injecting prior results into context."""
        agent = self.agents[agent_key]
        agent_input = {**context, "prior_results": {k: v.payload for k, v in prior_results.items()}}
        try:
            return await agent.execute(agent_input)
        except Exception as e:
            self.logger.error(f"Agent {agent_key} failed: {e}")
            return AgentMessage(
                from_agent=agent_key,
                to_agent="orchestrator",
                message_type="error",
                payload={"error": str(e)},
            )

    def _assemble_output(self, results: Dict[str, AgentMessage], elapsed_ms: int) -> Dict[str, Any]:
        """Reconcile all agent outputs into final response."""
        writing_result = results.get("writing", AgentMessage("", "", "", {})).payload
        citation_result = results.get("citation", AgentMessage("", "", "", {})).payload
        integrity_result = results.get("integrity", AgentMessage("", "", "", {})).payload
        retrieval_result = results.get("retrieval", AgentMessage("", "", "", {})).payload
        review_result = results.get("literature_review", AgentMessage("", "", "", {})).payload

        return {
            "generated_output": writing_result.get("draft", ""),
            "cited_output": citation_result.get("cited_text", writing_result.get("draft", "")),
            "bibliography": citation_result.get("reference_list", []),
            "citation_map": citation_result.get("citation_map", []),
            "sources": retrieval_result.get("sources", []),
            "evidence_traces": citation_result.get("evidence_traces", []),
            "integrity_status": integrity_result.get("integrity_status", "pending"),
            "integrity_report": integrity_result,
            "review_structure": review_result.get("themes", []),
            "word_count": writing_result.get("word_count", 0),
            "readability_score": writing_result.get("readability_score"),
            "style_match_score": writing_result.get("style_match_score"),
            "model_used": writing_result.get("model_used"),
            "processing_time_ms": elapsed_ms,
        }
