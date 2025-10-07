import os
import motor.motor_asyncio
from beanie import init_beanie, Document
from dotenv import load_dotenv
import inspect
import client_service.schemas as schemas

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Async MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# Collect all Beanie Document subclasses from schemas
document_models = [
    cls for name, cls in inspect.getmembers(schemas, inspect.isclass)
    if issubclass(cls, Document) and cls is not Document
]



async def init_db():
    """Initialize Beanie with all document models"""
    await init_beanie(database=db, document_models=document_models)
    return db


async def get_db():
    """Get database instance"""
    return db

def get_mongo_db():
    """Get database instance (sync wrapper)"""
    return db
