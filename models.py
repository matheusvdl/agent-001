from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TicketCategory(str, Enum):
    billing = "billing"
    technical = "technical"
    general = "general"
    complaint = "complaint"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    error = "error"


class TicketInput(BaseModel):
    title: str
    description: str
    customer_id: str


class AnalysisResult(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    needs_human: bool
    suggested_reply: str
    next_action: str


class ChatInput(BaseModel):
    run_id: str
    message: str


class RunResponse(BaseModel):
    run_id: str
    status: RunStatus
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None
