from contextlib import asynccontextmanager

import uvicorn
from etl_service.api.routes.routers import api_router
from etl_service.config import settings
from etl_service.services.browser_service import BrowserService
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown lifecycle."""
    # Startup logic (if any)
    try:
        # Example: await BrowserService.init_browser()
        yield
    finally:
        # Ensure browser is closed on shutdown
        await BrowserService.close_browser()


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    app = FastAPI(
        title="SupplyNote GRN Report Automation",
        description="Automated ETL service for SupplyNote GRN reports",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(api_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ETL service is running"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "etl_service.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
        reload=True,  # Optional: disable in production
    )
