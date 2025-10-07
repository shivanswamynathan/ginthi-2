

"""
Import all models and rebuild them to resolve forward references.
This ensures that all Link relationships work properly and that
FastAPI can generate the OpenAPI schema correctly.
"""

from client_service.schemas.client_db.client_models import Clients, CentralClients, ClientEntity
from client_service.schemas.client_db.user_models import Users, Roles, Permissions, UserRoles, RolePermissions, UserLog
from client_service.schemas.client_db.vendor_models import VendorMaster, VendorTransactions, TransactionLog, ActionLog
from client_service.schemas.client_db.item_models import ItemMaster
from client_service.schemas.client_db.workflow_models import WorkflowRequestLedger

# Rebuild all models to resolve forward references
# This must happen AFTER all models are imported
CentralClients.model_rebuild()
Clients.model_rebuild()
ClientEntity.model_rebuild()
Roles.model_rebuild()
Permissions.model_rebuild()
RolePermissions.model_rebuild()
Users.model_rebuild()
UserRoles.model_rebuild()
UserLog.model_rebuild()
VendorMaster.model_rebuild()
VendorTransactions.model_rebuild()
ActionLog.model_rebuild()
TransactionLog.model_rebuild()
ItemMaster.model_rebuild()
WorkflowRequestLedger.model_rebuild()

__all__ = [
    "Clients",
    "CentralClients",
    "ClientEntity",
    "Users",
    "Roles",
    "Permissions",
    "UserRoles",
    "RolePermissions",
    "UserLog",
    "VendorMaster",
    "VendorTransactions",
    "TransactionLog",
    "ActionLog",
    "ItemMaster",
    "WorkflowRequestLedger"
]
