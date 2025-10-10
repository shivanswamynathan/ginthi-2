# api/routes/__init__.py
from .central_clients_router import router as central_clients_router
from .clients_router import router as clients_router
from .entities_router import router as entities_router
from .items_router import router as items_router
from .logs_router import router as logs_router
from .permissions_router import router as permissions_router
from .role_permissions_router import router as role_permissions_router
from .roles_router import router as roles_router
from .transactions_router import router as transactions_router
from .user_roles_router import router as user_roles_router
from .users_router import router as users_router
from .vendors_router import router as vendors_router
from .workflows_router import router as workflows_router

__all__ = [
    'central_clients_router', 'clients_router', 'entities_router', 'items_router',
    'logs_router', 'permissions_router', 'role_permissions_router', 'roles_router',
    'transactions_router', 'user_roles_router', 'users_router', 'vendors_router',
    'workflows_router'
]