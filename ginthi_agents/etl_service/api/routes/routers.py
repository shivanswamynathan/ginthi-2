from etl_service.api.routes import po_router, report_routes
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(
    report_routes.router, prefix="/api/v1/supply_note/reports", tags=["GRN Reports"]
)
api_router.include_router(
    po_router.router,
    prefix="/api/v1/supply_note/reports",
    tags=["Purchase Order Reports"],
)
