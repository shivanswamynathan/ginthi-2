from fastapi import APIRouter
from client_service.api import (
    clients_router,
    users_router,
    vendors_router,
    transactions_router,
    entities_router,
    roles_router,
    permissions_router,
    items_router,
    workflows_router,
    user_roles_router,
    role_permissions_router,
    logs_router,
    central_clients_router
)

api_router = APIRouter()

# Include all routers
api_router.include_router(clients_router.router, prefix="/api/v1", tags=["Clients"])
api_router.include_router(central_clients_router.router, prefix="/api/v1", tags=["Central Clients"])
api_router.include_router(entities_router.router, prefix="/api/v1", tags=["Client Entities"])
api_router.include_router(users_router.router, prefix="/api/v1", tags=["Users"])
api_router.include_router(roles_router.router, prefix="/api/v1", tags=["Roles"])
api_router.include_router(permissions_router.router, prefix="/api/v1", tags=["Permissions"])
api_router.include_router(user_roles_router.router, prefix="/api/v1", tags=["User Roles"])
api_router.include_router(role_permissions_router.router, prefix="/api/v1", tags=["Role Permissions"])
api_router.include_router(vendors_router.router, prefix="/api/v1", tags=["Vendors"])
api_router.include_router(transactions_router.router, prefix="/api/v1", tags=["Transactions"])
api_router.include_router(items_router.router, prefix="/api/v1", tags=["Items"])
api_router.include_router(workflows_router.router, prefix="/api/v1", tags=["Workflows"])
api_router.include_router(logs_router.router, prefix="/api/v1", tags=["Logs"])