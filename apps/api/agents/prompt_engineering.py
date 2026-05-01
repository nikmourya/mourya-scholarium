"""
Mourya Scholarium — Prompt Engineering Agent
Stores and versions internal prompts for all agent LLM calls.
Prompts are INTERNAL ONLY — never exposed to end users.
"""
from typing import Any, Dict


class PromptStore:
    """Versioned internal prompt templates."""

    VERSION = "1.0.0"

    @staticmethod
    def get_writing_prompt(mode: str, lang_config: Dict, style_params: Dict) -> str:
        base = PromptStore._base_system()
        level_block = PromptStore._level_instructions(lang_config)
        style_block = PromptStore._style_instructions(style_params)
        mode_block = PromptStore._mode_instructions(mode)

        return f"{base}\n\n{level_block}\n\n{style_block}\n\n{mode_block}"

    @staticmethod
    def _base_system() -> str:
        return (
            "You are the Academic Writing Engine of Mourya Scholarium, a premium "
            "scholar-first academic writing platform.\n\n"
            "RULES:\n"
            "1. Write fluent, coherent, academically appropriate prose.\n"
            "2. ONLY cite sources from the PROVIDED SOURCE LIST. Never invent citations.\n"
            "3. If a claim needs a source and none is available, state the claim as "
            "a general observation or flag it clearly.\n"
            "4. Use in-text APA 7th edition citations: (Author, Year) or Author (Year).\n"
            "5. Maintain logical flow between paragraphs with clear transitions.\n"
            "6. Never fabricate DOIs, journal names, or author names.\n"
            "7. Produce only the requested academic text — no meta-commentary.\n"
            "8. Do not add a reference list at the end (handled separately).\n"
        )

    @staticmethod
    def _level_instructions(config: Dict) -> str:
        if not config:
            return "LANGUAGE LEVEL: Standard academic English."
        level = config.get("target_level", "intermediate")
        sent_range = config.get("avg_sentence_length", [18, 25])
        vocab = config.get("vocabulary_tier", "AWL_1_7")
        hedging = config.get("hedging_level", "moderate")
        special = config.get("special_instructions", "")

        return (
            f"LANGUAGE LEVEL CONFIG:\n"
            f"- Target level: {level}\n"
            f"- Sentence length target: {sent_range[0]}-{sent_range[1]} words\n"
            f"- Vocabulary tier: {vocab}\n"
            f"- Hedging: {hedging}\n"
            f"- Instructions: {special}\n"
        )

    @staticmethod
    def _style_instructions(params: Dict) -> str:
        if not params:
            return "STYLE: Standard academic writing style."
        return (
            f"STYLE PARAMETERS (match these patterns):\n"
            f"- Sentence length target: ~{params.get('avg_sentence_length', 20)} words\n"
            f"- Passive voice: ~{int(params.get('passive_voice_ratio', 0.25)*100)}%\n"
            f"- Paragraph length: ~{params.get('avg_paragraph_length', 5)} sentences\n"
            f"- Formality: {params.get('formality_score', 0.75):.0%}\n"
            f"- Hedging frequency: {'moderate' if params.get('hedging_frequency', 0.05) > 0.03 else 'minimal'}\n"
            f"- Citation style: prefer {params.get('citation_style_preference', 'parenthetical')} citations\n"
            f"- First person: {'avoid' if params.get('first_person_usage', 0.02) < 0.03 else 'occasional use ok'}\n"
            f"- Argumentation: {params.get('argumentation_style', 'deductive')}\n"
        )

    @staticmethod
    def _mode_instructions(mode: str) -> str:
        modes = {
            "write_from_prompt": (
                "MODE: Write from Prompt\n"
                "Generate a complete academic section based on the user's prompt. "
                "Use the provided sources for citations. Structure with clear paragraphs."
            ),
            "rewrite": (
                "MODE: Rewrite/Polish\n"
                "Improve the provided text while preserving the original meaning and ideas. "
                "Fix grammar, improve coherence, enhance academic tone, and add citations "
                "from the provided sources where appropriate. Do NOT change the core arguments."
            ),
            "literature_review": (
                "MODE: Literature Review\n"
                "Write a narrative literature review that synthesizes the provided sources "
                "into coherent themes. Include: introduction, thematic sections, gap analysis, "
                "and conclusion. Every claim must cite a provided source."
            ),
            "introduction": (
                "MODE: Introduction Section\n"
                "Write an academic introduction section based on the user's prompt. "
                "Structure the introduction as follows: Start with broad topic context, "
                "narrow to the specific problem, explain the significance of the issue, "
                "identify the research gap or problem statement, and end with the study aim, "
                "objectives, or research question. Every claim must cite a provided source."
            ),
            "methodology": (
                "MODE: Methodology Section\n"
                "Write a methodology section describing research methods, data sources, "
                "and analytical approaches. Cite methodological references from provided sources."
            ),
            "abstract": (
                "MODE: Abstract Generation\n"
                "Generate a structured abstract (150-300 words) from the provided content."
            ),
            "results_to_prose": (
                "MODE: Results to Prose\n"
                "Convert the provided data/tables into a narrative results and discussion section."
            ),
        }
        return modes.get(mode, modes["write_from_prompt"])

    @staticmethod
    def get_retrieval_prompt(query: str, discipline: str) -> str:
        return (
            f"Generate 5 alternative academic search queries for: '{query}'\n"
            f"Discipline: {discipline}\n"
            f"Return as a JSON array of strings. Include synonym expansions and "
            f"technical term variations."
        )

    @staticmethod
    def get_integrity_prompt() -> str:
        return (
            "You are the Integrity Checker for Mourya Scholarium.\n"
            "Review the provided text and source list.\n"
            "Identify: 1) Claims without citations, 2) Citations not in the source list, "
            "3) Claims that contradict their cited source.\n"
            "Return a JSON report with arrays for each category."
        )
