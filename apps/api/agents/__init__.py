"""
Mourya Scholarium — Agent Base Classes
All agents inherit from BaseAgent and follow a consistent interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger("mourya.agents")


class AgentMessage:
    """Structured message for inter-agent communication."""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
    ):
        self.message_id = str(uuid.uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.task_id = task_id or str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.status = "pending"
        self.confidence = 1.0
        self.warnings: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "confidence": self.confidence,
            "warnings": self.warnings,
            "payload": self.payload,
        }


class BaseAgent(ABC):
    """Base class for all Mourya Scholarium agents."""

    agent_name: str = "base"

    def __init__(self):
        self.logger = logging.getLogger(f"mourya.agents.{self.agent_name}")

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> AgentMessage:
        """Execute the agent's primary responsibility."""
        pass

    def create_response(
        self,
        to_agent: str,
        payload: Dict[str, Any],
        task_id: str = "",
        status: str = "completed",
        confidence: float = 1.0,
        warnings: Optional[List[str]] = None,
    ) -> AgentMessage:
        msg = AgentMessage(
            from_agent=self.agent_name,
            to_agent=to_agent,
            message_type="task_result",
            payload=payload,
            task_id=task_id,
        )
        msg.status = status
        msg.confidence = confidence
        msg.warnings = warnings or []
        return msg
