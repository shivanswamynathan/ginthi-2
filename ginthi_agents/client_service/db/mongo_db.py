import os
import motor.motor_asyncio
from beanie import init_beanie, Document
from dotenv import load_dotenv
import inspect
import client_service.schemas.client_db as schemas_module

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Async MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]


def get_document_models():
    """
    Auto-discover all Beanie Document models from the schemas module.
    This eliminates the need to manually maintain a list of models.
    """
    document_models = []
    
    # Get all classes from the schemas module
    for name, obj in inspect.getmembers(schemas_module, inspect.isclass):
        # Check if it's a Document subclass (but not Document itself)
        if issubclass(obj, Document) and obj is not Document:
            document_models.append(obj)
    
    return document_models


async def init_db():
    """
    Initialize Beanie with all document models.
    Collections will be created automatically when documents are inserted.
    """
    document_models = get_document_models()
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