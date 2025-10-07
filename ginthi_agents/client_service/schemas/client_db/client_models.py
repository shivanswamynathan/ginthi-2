from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Clients(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    ClientID: int
    ClientName: str
    CentralClientID: Optional[int] = None
    CentralAPIKey: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=datetime.utcnow)
    UpdatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "ClientID": 1,
                "ClientName": "ABC Corporation",
                "CentralClientID": 100,
                "CentralAPIKey": "api_key_xyz"
            }
        }

class CentralClients(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    ClientID: int
    Name: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ClientEntity(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    ClientID: int
    EntityID: int
    GSTID: Optional[str] = None
    CompanyPan: Optional[str] = None
    EntityName: str
    TAN: Optional[str] = None
    ParentClientID: Optional[int] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}