"""
Constants file for all API response messages.
Similar to Django's approach of centralizing messages.
"""


class CentralClientMessages:
    """Messages for Central Client operations"""
    
    # Success messages
    CREATED_SUCCESS = "Central client created successfully: {name}"
    RETRIEVED_SUCCESS = "Central client retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} central clients"
    UPDATED_SUCCESS = "Central client updated: {name}"
    DELETED_SUCCESS = "Central client {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Central client with ID {id} not found"
    CREATE_ERROR = "Error creating central client: {error}"
    RETRIEVE_ERROR = "Error retrieving central client: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving central clients: {error}"
    UPDATE_ERROR = "Error updating central client: {error}"
    DELETE_ERROR = "Error deleting central client: {error}"


class ClientMessages:
    """Messages for Client operations"""
    
    # Success messages
    CREATED_SUCCESS = "Client created successfully: {name}"
    RETRIEVED_SUCCESS = "Client retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} clients"
    UPDATED_SUCCESS = "Client updated: {name}"
    DELETED_SUCCESS = "Client {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Client with ID {id} not found"
    DUPLICATE_NAME = "Client with name '{name}' already exists"
    CREATE_ERROR = "Error creating client: {error}"
    RETRIEVE_ERROR = "Error retrieving client: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving clients: {error}"
    UPDATE_ERROR = "Error updating client: {error}"
    DELETE_ERROR = "Error deleting client: {error}"


class EntityMessages:
    """Messages for Client Entity operations"""
    
    # Success messages
    CREATED_SUCCESS = "Entity created successfully: {name}"
    RETRIEVED_SUCCESS = "Entity retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} entities"
    RETRIEVED_BY_CLIENT_SUCCESS = "Retrieved {count} entities for client {id}"
    UPDATED_SUCCESS = "Entity updated: {name}"
    DELETED_SUCCESS = "Entity {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Entity with ID {id} not found"
    CLIENT_NOT_FOUND = "Client with ID {id} not found"
    NO_ENTITIES_FOR_CLIENT = "No entities found for client {id}"
    CREATE_ERROR = "Error creating entity: {error}"
    RETRIEVE_ERROR = "Error retrieving entity: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving entities: {error}"
    UPDATE_ERROR = "Error updating entity: {error}"
    DELETE_ERROR = "Error deleting entity: {error}"


class UserMessages:
    """Messages for User operations"""
    
    # Success messages
    CREATED_SUCCESS = "User created successfully: {name}"
    RETRIEVED_SUCCESS = "User retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} users"
    UPDATED_SUCCESS = "User updated: {name}"
    DELETED_SUCCESS = "User {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "User with ID {id} not found"
    DUPLICATE_EMAIL = "User with email '{email}' already exists"
    CREATE_ERROR = "Error creating user: {error}"
    RETRIEVE_ERROR = "Error retrieving user: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving users: {error}"
    UPDATE_ERROR = "Error updating user: {error}"
    DELETE_ERROR = "Error deleting user: {error}"


class RoleMessages:
    """Messages for Role operations"""
    
    # Success messages
    CREATED_SUCCESS = "Role created successfully: {name}"
    RETRIEVED_SUCCESS = "Role retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} roles"
    UPDATED_SUCCESS = "Role updated: {name}"
    DELETED_SUCCESS = "Role {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Role with ID {id} not found"
    DUPLICATE_NAME = "Role with name '{name}' already exists"
    CREATE_ERROR = "Error creating role: {error}"
    RETRIEVE_ERROR = "Error retrieving role: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving roles: {error}"
    UPDATE_ERROR = "Error updating role: {error}"
    DELETE_ERROR = "Error deleting role: {error}"


class PermissionMessages:
    """Messages for Permission operations"""
    
    # Success messages
    CREATED_SUCCESS = "Permission created successfully: {name}"
    RETRIEVED_SUCCESS = "Permission retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} permissions"
    UPDATED_SUCCESS = "Permission updated: {name}"
    DELETED_SUCCESS = "Permission {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Permission with ID {id} not found"
    DUPLICATE_NAME = "Permission with name '{name}' already exists"
    CREATE_ERROR = "Error creating permission: {error}"
    RETRIEVE_ERROR = "Error retrieving permission: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving permissions: {error}"
    UPDATE_ERROR = "Error updating permission: {error}"
    DELETE_ERROR = "Error deleting permission: {error}"


class VendorMessages:
    """Messages for Vendor operations"""
    
    # Success messages
    CREATED_SUCCESS = "Vendor created successfully: {name}"
    RETRIEVED_SUCCESS = "Vendor retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} vendors"
    UPDATED_SUCCESS = "Vendor updated: {name}"
    DELETED_SUCCESS = "Vendor {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Vendor with ID {id} not found"
    DUPLICATE_CODE = "Vendor with code '{code}' already exists"
    CREATE_ERROR = "Error creating vendor: {error}"
    RETRIEVE_ERROR = "Error retrieving vendor: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving vendors: {error}"
    UPDATE_ERROR = "Error updating vendor: {error}"
    DELETE_ERROR = "Error deleting vendor: {error}"


class TransactionMessages:
    """Messages for Transaction operations"""
    
    # Success messages
    CREATED_SUCCESS = "Transaction created successfully: {invoice}"
    RETRIEVED_SUCCESS = "Transaction retrieved: {invoice}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} transactions"
    RETRIEVED_BY_VENDOR_SUCCESS = "Retrieved {count} transactions for vendor {id}"
    UPDATED_SUCCESS = "Transaction updated: {invoice}"
    DELETED_SUCCESS = "Transaction {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Transaction with ID {id} not found"
    VENDOR_NOT_FOUND = "Vendor with ID {id} not found"
    DUPLICATE_INVOICE = "Transaction with InvoiceID '{invoice}' already exists"
    NO_TRANSACTIONS_FOR_VENDOR = "No transactions found for vendor {id}"
    CREATE_ERROR = "Error creating transaction: {error}"
    RETRIEVE_ERROR = "Error retrieving transaction: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving transactions: {error}"
    UPDATE_ERROR = "Error updating transaction: {error}"
    DELETE_ERROR = "Error deleting transaction: {error}"


class ItemMessages:
    """Messages for Item operations"""
    
    # Success messages
    CREATED_SUCCESS = "Item created successfully: {name}"
    RETRIEVED_SUCCESS = "Item retrieved: {name}"
    RETRIEVED_BY_CODE_SUCCESS = "Item retrieved by code: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} items"
    UPDATED_SUCCESS = "Item updated: {name}"
    DELETED_SUCCESS = "Item {id} deleted successfully"
    
    # Error messages
    NOT_FOUND = "Item with ID {id} not found"
    NOT_FOUND_BY_CODE = "Item with code '{code}' not found"
    DUPLICATE_CODE = "Item with code '{code}' already exists"
    CREATE_ERROR = "Error creating item: {error}"
    RETRIEVE_ERROR = "Error retrieving item: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving items: {error}"
    UPDATE_ERROR = "Error updating item: {error}"
    DELETE_ERROR = "Error deleting item: {error}"


class WorkflowMessages:
    """Messages for Workflow operations"""
    
    # Success messages
    CREATED_SUCCESS = "Workflow ledger created successfully: {name}"
    RETRIEVED_SUCCESS = "Workflow ledger retrieved: {name}"
    RETRIEVED_ALL_SUCCESS = "Retrieved {count} workflow ledgers"
    RETRIEVED_BY_CLIENT_SUCCESS = "Retrieved {count} workflow ledgers for client {id}"
    RETRIEVED_BY_USER_SUCCESS = "Retrieved {count} workflow ledgers for user {id}"
    UPDATED_SUCCESS = "Workflow ledger updated: {name}"
    DELETED_SUCCESS = "Workflow ledger {id} deleted successfully"
    REQUEST_INCREMENTED = "Request count incremented"
    
    # Error messages
    NOT_FOUND = "Workflow ledger with ID {id} not found"
    CLIENT_NOT_FOUND = "Client with ID {id} not found"
    USER_NOT_FOUND = "User with ID {id} not found"
    NO_WORKFLOWS_FOR_CLIENT = "No workflow ledgers found for client {id}"
    NO_WORKFLOWS_FOR_USER = "No workflow ledgers found for user {id}"
    CREATE_ERROR = "Error creating workflow ledger: {error}"
    RETRIEVE_ERROR = "Error retrieving workflow ledger: {error}"
    RETRIEVE_ALL_ERROR = "Error retrieving workflow ledgers: {error}"
    UPDATE_ERROR = "Error updating workflow ledger: {error}"
    DELETE_ERROR = "Error deleting workflow ledger: {error}"
    INCREMENT_ERROR = "Error incrementing workflow request: {error}"


class UserRoleMessages:
    """Messages for User Role operations"""
    
    # Success messages
    ASSIGNED_SUCCESS = "Role {role_name} assigned to user {user_name}"
    RETRIEVED_USER_ROLES_SUCCESS = "Retrieved {count} roles for user {id}"
    RETRIEVED_ROLE_USERS_SUCCESS = "Retrieved {count} users with role {id}"
    REMOVED_SUCCESS = "Role {role_id} removed from user {user_id} successfully"
    
    # Error messages
    USER_NOT_FOUND = "User with ID {id} not found"
    ROLE_NOT_FOUND = "Role with ID {id} not found"
    ALREADY_ASSIGNED = "User {user_id} already has role {role_id}"
    ASSIGNMENT_NOT_FOUND = "Role assignment not found for user {user_id} and role {role_id}"
    NO_ROLES_FOR_USER = "No roles found for user {id}"
    NO_USERS_FOR_ROLE = "No users found with role {id}"
    ASSIGN_ERROR = "Error assigning role to user: {error}"
    RETRIEVE_ERROR = "Error retrieving user roles: {error}"
    REMOVE_ERROR = "Error removing role from user: {error}"


class RolePermissionMessages:
    """Messages for Role Permission operations"""
    
    # Success messages
    ASSIGNED_SUCCESS = "Permission {permission_name} assigned to role {role_name}"
    RETRIEVED_ROLE_PERMISSIONS_SUCCESS = "Retrieved {count} permissions for role {id}"
    RETRIEVED_PERMISSION_ROLES_SUCCESS = "Retrieved {count} roles with permission {id}"
    REMOVED_SUCCESS = "Permission {permission_id} removed from role {role_id} successfully"
    
    # Error messages
    ROLE_NOT_FOUND = "Role with ID {id} not found"
    PERMISSION_NOT_FOUND = "Permission with ID {id} not found"
    ALREADY_ASSIGNED = "Role {role_id} already has permission {permission_id}"
    ASSIGNMENT_NOT_FOUND = "Permission assignment not found for role {role_id} and permission {permission_id}"
    NO_PERMISSIONS_FOR_ROLE = "No permissions found for role {id}"
    NO_ROLES_FOR_PERMISSION = "No roles found with permission {id}"
    ASSIGN_ERROR = "Error assigning permission to role: {error}"
    RETRIEVE_ERROR = "Error retrieving role permissions: {error}"
    REMOVE_ERROR = "Error removing permission from role: {error}"


class LogMessages:
    """Messages for Log operations"""
    
    # Success messages
    ACTION_LOG_CREATED = "Action log created successfully: LogId {id}"
    TRANSACTION_LOG_CREATED = "Transaction log created successfully: LogID {id}"
    USER_LOG_CREATED = "User log created successfully: LogId {id}"
    LOG_RETRIEVED = "Log retrieved: {id}"
    LOGS_RETRIEVED = "Retrieved {count} logs"
    LOGS_BY_TRANSACTION_RETRIEVED = "Retrieved {count} logs for transaction {id}"
    LOGS_BY_USER_RETRIEVED = "Retrieved {count} logs for user {id}"
    
    # Error messages
    LOG_NOT_FOUND = "Log with ID {id} not found"
    NO_LOGS_FOR_TRANSACTION = "No logs found for transaction {id}"
    NO_LOGS_FOR_USER = "No logs found for user {id}"
    CREATE_ERROR = "Error creating log: {error}"
    RETRIEVE_ERROR = "Error retrieving log: {error}"