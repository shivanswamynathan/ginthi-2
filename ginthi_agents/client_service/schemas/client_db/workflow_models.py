from beanie import Document
from pydantic import Field
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone


class WorkflowRequestLedger(Document):
    LedgerID: int
    ClientID: int
    UserID: int
    WorkflowName: str
    RequestCount: int = 0
    LastRequestAt: Optional[datetime] = None
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "workflow_request_ledger"