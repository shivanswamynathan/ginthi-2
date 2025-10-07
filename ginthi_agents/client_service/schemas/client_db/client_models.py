from beanie import Document,Link
from pydantic import Field
from typing import Optional,TYPE_CHECKING
from datetime import datetime, timezone


class CentralClients(Document):
    ClientID: int
    Name: str

    class Settings:
        name = "central_clients"

class Clients(Document):
    ClientID: int
    ClientName: str
    CentralClientID: Optional[int] = None
    CentralAPIKey: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    central_client: Optional[Link[CentralClients]] = None

    class Settings:
        name = "clients"


class ClientEntity(Document):
    ClientID: int
    EntityID: int
    GSTID: Optional[str] = None
    CompanyPan: Optional[str] = None
    EntityName: str
    TAN: Optional[str] = None
    ParentClientID: Optional[int] = None

    client: Optional[Link[Clients]] = None
    parent_client_entity: Optional[Link["ClientEntity"]] = None

    class Settings:
        name = "client_entity"
