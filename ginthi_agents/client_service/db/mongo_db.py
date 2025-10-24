import os
import motor.motor_asyncio
from beanie import init_beanie
from dotenv import load_dotenv
from client_service.schemas.mongo_schemas.client_schema_model import ClientSchema

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Async MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]


async def init_db():
    """
    Initialize Beanie with all document models.
    """
    # Import models here to avoid circular imports
    
    
    document_models = [ClientSchema]  # Add all your Document models here
    
    print(f"Initializing Beanie with {len(document_models)} models:")
    for model in document_models:
        print(f"  - {model.__name__}")
    
    await init_beanie(database=db, document_models=document_models)
    return db


async def get_db():
    """Get database instance"""
    return db


def get_mongo_db():
    """Get database instance (sync wrapper)"""
    return db