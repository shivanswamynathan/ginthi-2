from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime, timezone

class ItemMaster(Document):
    ItemID: int
    ItemCode: str
    ItemName: str
    HSNCode: Optional[str] = None
    Description: Optional[str] = None
    UnitMeasurement: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "item_master"