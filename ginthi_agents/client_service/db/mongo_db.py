from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Async MongoDB client (for FastAPI)
async_mongo_client = AsyncIOMotorClient(MONGO_URI)
async_database = async_mongo_client[MONGO_DB]


# Get database
def get_mongo_db():

    return async_database
