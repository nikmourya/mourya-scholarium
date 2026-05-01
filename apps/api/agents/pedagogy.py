"""
Mourya Scholarium — Writing Pedagogy Agent
Maps user English level → LanguageLevelConfig controlling readability,
vocabulary, sentence complexity, and hedging style.
"""
from typing import Any, Dict
from agents import BaseAgent, AgentMessage

LEVEL_CONFIGS = {
    "beginner": {
        "target_level": "beginner",
        "avg_sentence_length": [12, 18],
        "vocabulary_tier": "AWL_1_4",
        "sentence_complexity": "simple",
        "hedging_level": "minimal",
        "readability_target": [50, 60],
        "special_instructions": "Use short clear sentences. Avoid jargon. Explain technical terms.",
    },
    "intermediate": {
        "target_level": "intermediate",
        "avg_sentence_length": [18, 25],
        "vocabulary_tier": "AWL_1_7",
        "sentence_complexity": "mixed",
        "hedging_level": "moderate",
        "readability_target": [35, 50],
        "special_instructions": "Use standard academic language. Mix simple and complex sentences.",
    },
    "advanced": {
        "target_level": "advanced",
        "avg_sentence_length": [22, 30],
        "vocabulary_tier": "full_academic",
        "sentence_complexity": "complex",
        "hedging_level": "sophisticated",
        "readability_target": [25, 35],
        "special_instructions": "Use full academic vocabulary including discipline-specific terms. Varied syntax.",
    },
    "publication_ready": {
        "target_level": "publication_ready",
        "avg_sentence_length": [15, 35],
        "vocabulary_tier": "journal_standard",
        "sentence_complexity": "varied",
        "hedging_level": "field_standard",
        "readability_target": [20, 30],
        "special_instructions": "Produce journal-quality prose. Precise terminology. Intentional rhythm.",
    },
}


class PedagogyAgent(BaseAgent):
    agent_name = "pedagogy"

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        profile = task.get("user_profile", {})
        english_level = profile.get("english_level", "intermediate")
        academic_level = profile.get("academic_level", "postgraduate")

        config = LEVEL_CONFIGS.get(english_level, LEVEL_CONFIGS["intermediate"]).copy()
        config["academic_level"] = academic_level

        # Adjust for target output level
        target = profile.get("target_output_level", "match_current")
        if target == "elevate_slightly":
            levels = list(LEVEL_CONFIGS.keys())
            idx = levels.index(english_level) if english_level in levels else 1
            if idx < len(levels) - 1:
                elevated = LEVEL_CONFIGS[levels[idx + 1]]
                config["readability_target"] = elevated["readability_target"]
                config["vocabulary_tier"] = elevated["vocabulary_tier"]
        elif target == "publication_ready":
            pub = LEVEL_CONFIGS["publication_ready"]
            config["readability_target"] = pub["readability_target"]
            config["vocabulary_tier"] = pub["vocabulary_tier"]
            config["hedging_level"] = pub["hedging_level"]

        return self.create_response(
            to_agent="orchestrator",
            payload={"language_level_config": config},
        )
