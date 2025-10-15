from fastapi import FastAPI
from client_service.api.routes.routes import api_router
from client_service.utils import register_exception_handlers, setup_logging
from client_service.utils.lifespan import lifespan
import uvicorn
import os

from dotenv import load_dotenv

load_dotenv()


# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", None)
)

# Create FastAPI application
app = FastAPI(
    title="Client Service API",
    version="1.0.0",
    description="PostgreSQL-based Client Service API",
    lifespan=lifespan
)

# Register exception handlers
register_exception_handlers(app)

# Include all API routes
app.include_router(api_router)


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


def main():
    """
    Main function to run the application with uvicorn.
    """
    uvicorn.run(
        "client_service.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8005)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        workers=int(os.getenv("WORKERS", 1))
    )


if __name__ == "__main__":
    main()
