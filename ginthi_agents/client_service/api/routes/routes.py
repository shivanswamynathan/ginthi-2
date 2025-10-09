from fastapi import APIRouter
from . import (  # Import from the current package (api/routes/)
    central_clients_router, clients_router, entities_router, items_router,
    logs_router, permissions_router, role_permissions_router, roles_router,
    transactions_router, user_roles_router, users_router, vendors_router, workflows_router
)

api_router = APIRouter()

# Include all routers
api_router.include_router(clients_router, prefix="/api/v1", tags=["Clients"])
api_router.include_router(central_clients_router, prefix="/api/v1", tags=["Central Clients"])
api_router.include_router(entities_router, prefix="/api/v1", tags=["Client Entities"])
api_router.include_router(users_router, prefix="/api/v1", tags=["Users"])
api_router.include_router(roles_router, prefix="/api/v1", tags=["Roles"])
api_router.include_router(permissions_router, prefix="/api/v1", tags=["Permissions"])
api_router.include_router(user_roles_router, prefix="/api/v1", tags=["User Roles"])
api_router.include_router(role_permissions_router, prefix="/api/v1", tags=["Role Permissions"])
api_router.include_router(vendors_router, prefix="/api/v1", tags=["Vendors"])
api_router.include_router(transactions_router, prefix="/api/v1", tags=["Transactions"])
api_router.include_router(items_router, prefix="/api/v1", tags=["Items"])
api_router.include_router(workflows_router, prefix="/api/v1", tags=["Workflows"])
api_router.include_router(logs_router, prefix="/api/v1", tags=["Logs"])