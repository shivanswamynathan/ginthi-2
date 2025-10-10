from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from client_service.db.postgres_db import init_db, close_db
from client_service.api.routes.routes import api_router
from client_service.api.constants.status_codes import StatusCode
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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle all HTTPException errors and return uniform APIResponse format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions and return uniform APIResponse format
    """
    logging.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=StatusCode.INTERNAL_SERVER_ERROR, 
        content={
            "success": False,
            "message": "Internal server error",
            "data": None
        }
    )


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Client Service API is running with PostgreSQL",
        "data": {
            "version": "1.0.0",
            "database": "PostgreSQL"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "Service is healthy",
        "data": {
            "status": "healthy",
            "database": "PostgreSQL"
        }
    }