from beanie import Document, Link
from pydantic import Field
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from client_service.schemas.client_db.client_models import Clients
    from client_service.schemas.client_db.user_models import Users

class WorkflowRequestLedger(Document):
    LedgerID: int
    ClientID: int
    UserID: int
    WorkflowName: str
    RequestCount: int = 0
    LastRequestAt: Optional[datetime] = None
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    client: Optional[Link["Clients"]] = None
    user: Optional[Link["Users"]] = None

    class Settings:
        name = "workflow_request_ledger"