"""
Mourya Scholarium — Style Learning Agent
Extracts writing-pattern features from user samples (never copies text verbatim).
Returns style parameters for controlled generation.
"""
import hashlib
import re
from typing import Any, Dict, List
from agents import BaseAgent, AgentMessage

# Hedge words and transition markers for feature extraction
HEDGE_WORDS = {"may", "might", "could", "suggests", "indicates", "appears", "seems",
               "possibly", "perhaps", "likely", "unlikely", "arguably", "potentially",
               "presumably", "apparently", "relatively", "generally", "typically"}

TRANSITION_WORDS = {"however", "therefore", "moreover", "furthermore", "nevertheless",
                    "consequently", "additionally", "meanwhile", "similarly", "conversely",
                    "specifically", "notably", "accordingly", "thus", "hence", "although",
                    "whereas", "in contrast", "for example", "in addition", "as a result"}

PASSIVE_PATTERNS = [
    r'\b(?:is|are|was|were|been|being)\s+\w+ed\b',
    r'\b(?:is|are|was|were|been|being)\s+\w+en\b',
]


class StyleLearningAgent(BaseAgent):
    agent_name = "style_learning"

    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        style_sig = task.get("style_signature")
        if style_sig:
            # Already computed — return existing signature as params
            return self.create_response(
                to_agent="orchestrator",
                payload={"style_params": style_sig},
            )
        # No pre-computed signature — return neutral defaults
        return self.create_response(
            to_agent="orchestrator",
            payload={"style_params": self._default_params()},
        )

    def analyze_sample(self, text: str) -> Dict[str, Any]:
        """Extract style features from a user writing sample. Called during onboarding."""
        sentences = self._split_sentences(text)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        words = text.split()
        word_count = len(words)

        if word_count < 20:
            return self._default_params()

        # Sentence length stats
        sent_lens = [len(s.split()) for s in sentences] if sentences else [15]
        avg_sent_len = sum(sent_lens) / len(sent_lens)
        variance = sum((l - avg_sent_len) ** 2 for l in sent_lens) / len(sent_lens) if len(sent_lens) > 1 else 0

        # Passive voice ratio
        passive_count = sum(1 for s in sentences if any(re.search(p, s, re.I) for p in PASSIVE_PATTERNS))
        passive_ratio = passive_count / len(sentences) if sentences else 0

        # Paragraph length
        sents_per_para = [len(self._split_sentences(p)) for p in paragraphs] if paragraphs else [4]
        avg_para_len = sum(sents_per_para) / len(sents_per_para)

        # Hedging frequency
        word_lower = [w.lower().strip(".,;:!?()[]") for w in words]
        hedge_count = sum(1 for w in word_lower if w in HEDGE_WORDS)
        hedge_freq = hedge_count / word_count if word_count else 0

        # Transition frequency
        text_lower = text.lower()
        trans_count = sum(1 for t in TRANSITION_WORDS if t in text_lower)
        trans_freq = trans_count / max(len(sentences), 1)

        # Formality heuristic (simplified F-score)
        formality = min(1.0, max(0.0, 0.5 + passive_ratio * 0.3 + (1 - hedge_freq) * 0.2))

        # First person usage
        first_person = sum(1 for w in word_lower if w in {"i", "we", "my", "our"})
        first_person_ratio = first_person / word_count if word_count else 0

        # Citation style detection
        parenthetical = len(re.findall(r'\([A-Z][a-z]+.*?\d{4}\)', text))
        narrative = len(re.findall(r'[A-Z][a-z]+\s+(?:et al\.\s+)?\(\d{4}\)', text))
        cite_style = "parenthetical" if parenthetical >= narrative else "narrative"

        return {
            "avg_sentence_length": round(avg_sent_len, 1),
            "sentence_length_variance": round(variance ** 0.5, 1),
            "passive_voice_ratio": round(passive_ratio, 2),
            "avg_paragraph_length": round(avg_para_len, 1),
            "vocabulary_sophistication": round(min(1.0, avg_sent_len / 30), 2),
            "hedging_frequency": round(hedge_freq, 3),
            "transition_frequency": round(trans_freq, 3),
            "formality_score": round(formality, 2),
            "citation_style_preference": cite_style,
            "argumentation_style": "deductive",
            "first_person_usage": round(first_person_ratio, 3),
            "sample_text_hash": hashlib.sha256(text.encode()).hexdigest(),
            "sample_word_count": word_count,
        }

    def _split_sentences(self, text: str) -> List[str]:
        parts = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in parts if len(s.strip()) > 5]

    def _default_params(self) -> Dict[str, Any]:
        return {
            "avg_sentence_length": 20.0,
            "sentence_length_variance": 5.0,
            "passive_voice_ratio": 0.25,
            "avg_paragraph_length": 5.0,
            "vocabulary_sophistication": 0.6,
            "hedging_frequency": 0.05,
            "transition_frequency": 0.08,
            "formality_score": 0.75,
            "citation_style_preference": "parenthetical",
            "argumentation_style": "deductive",
            "first_person_usage": 0.02,
        }
