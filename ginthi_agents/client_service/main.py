from fastapi import FastAPI
from contextlib import asynccontextmanager
from client_service.db.mongo_db import init_db
from client_service.api.routes import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Beanie
    await init_db()
    print("Database initialized successfully")
    yield
    # Shutdown
    print("Application shutting down")

app = FastAPI(
    title="Client Service API",
    version="1.0.0",
    lifespan=lifespan
)

# Include all API routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Client Service API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
