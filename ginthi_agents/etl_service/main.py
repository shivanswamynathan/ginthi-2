import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from etl_service.config import settings
from etl_service.api.routes.report_routes import router

app = FastAPI(
    title="SupplyNote GRN Report Automation",
    description="Automated ETL service for SupplyNote GRN reports",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    from ginthi_agents.etl_service.services.browser_service import BrowserService
    await BrowserService.close_browser()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    )