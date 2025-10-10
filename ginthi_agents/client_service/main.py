from fastapi import FastAPI
from contextlib import asynccontextmanager
from client_service.db.postgres_db import init_db, close_db
from client_service.api.routes.routes import api_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    await init_db()
    print("PostgreSQL Database initialized successfully")
    yield
    # Shutdown: Close database connections
    await close_db()
    print("Application shutting down")

app = FastAPI(
    title="Client Service API",
    version="1.0.0",
    description="PostgreSQL-based Client Service API",
    lifespan=lifespan
)

# Include all API routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Client Service API is running with PostgreSQL"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "PostgreSQL"}