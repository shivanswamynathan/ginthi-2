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

@app.get("/db-status")
async def check_db_status():
    """Check database connection and collections"""
    try:
        collections = await db.list_collection_names()
        return {
            "status": "connected",
            "database": db.name,
            "collections": collections,
            "total_collections": len(collections)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
