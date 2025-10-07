from fastapi import FastAPI
from contextlib import asynccontextmanager
from client_service.db.mongo_db import init_db, db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Database initialized successfully")
    
    # Print all collections after initialization
    collections = await db.list_collection_names()
    print(f"Collections in database: {collections}")
    
    yield
    print("Application shutting down")

app = FastAPI(
    title="Client Service API",
    version="1.0.0",
    lifespan=lifespan
)

