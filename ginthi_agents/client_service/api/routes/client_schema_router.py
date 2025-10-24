from fastapi import APIRouter, status, Depends  
from sqlalchemy.ext.asyncio import AsyncSession 
from client_service.api.dependencies import get_database_session 
from client_service.services.client_schema_service import ClientSchemaService
from client_service.schemas.base_response import APIResponse
from client_service.schemas.pydantic_schemas import (
    ClientSchemaCreate,
    ClientSchemaUpdate
)

router = APIRouter()


@router.post(
    "/client-schemas/create",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create client schema",
    description="Creates a new schema definition with versioning. Use when: 'create schema', 'define new schema', 'add document structure'.",
)
async def create_client_schema(
    schema_data: ClientSchemaCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Create a new client schema definition
    
    - Validates client exists in PostgreSQL
    - Auto-generates version if not provided
    - Deactivates other versions if is_active=True
    - Validates field types and references
    """
    return await ClientSchemaService.create(schema_data, db)  # ← ADDED db


@router.get(
    "/client-schemas/{schema_id}",
    response_model=APIResponse,
    summary="Get schema by ID",
    description="Retrieves schema by MongoDB ObjectId. Use when: 'get schema', 'show schema details', 'find schema by id'.",
)
async def get_client_schema(schema_id: str):
    """Get a client schema by MongoDB ObjectId"""
    return await ClientSchemaService.get_by_id(schema_id)


@router.get(
    "/client-schemas",
    response_model=APIResponse,
    summary="List all schemas",
    description="Get all client schemas with pagination. Use when: 'list schemas', 'show all schemas'.",
)
async def get_all_client_schemas(skip: int = 0, limit: int = 100):
    """Get all client schemas with pagination"""
    return await ClientSchemaService.get_all(skip, limit)


@router.get(
    "/client-schemas/client/{client_id}",
    response_model=APIResponse,
    summary="Get schemas by client",
    description="Get all schemas for a specific client. Use when: 'show client schemas', 'list schemas for client'.",
)
async def get_schemas_by_client(client_id: str):
    """Get all schemas for a specific client"""
    return await ClientSchemaService.get_by_client_id(client_id)


@router.get(
    "/client-schemas/client/{client_id}/{schema_name}",
    response_model=APIResponse,
    summary="Get schema by name",
    description="Get all versions of a schema by name for a client. Use when: 'show purchase_order schema', 'get invoice schema versions'.",
)
async def get_schema_by_name(client_id: str, schema_name: str):
    """Get all versions of a specific schema for a client"""
    return await ClientSchemaService.get_by_client_and_name(client_id, schema_name)


@router.get(
    "/client-schemas/client/{client_id}/{schema_name}/active",
    response_model=APIResponse,
    summary="Get active schema version",
    description="Get the currently active version of a schema. Use when: 'show active purchase_order schema', 'get current schema'.",
)
async def get_active_schema(client_id: str, schema_name: str):
    """Get the active version of a schema"""
    return await ClientSchemaService.get_active_schema(client_id, schema_name)


@router.put(
    "/client-schemas/{schema_id}",
    response_model=APIResponse,
    summary="Update schema",
    description="Updates schema definition in place. Use when: 'update schema', 'modify schema fields', 'change schema description'.",
)
async def update_client_schema(schema_id: str, schema_data: ClientSchemaUpdate):
    """
    Update a client schema
    
    - Updates the existing document
    - Can update description, fields, or is_active status
    - If activating, deactivates other versions
    """
    return await ClientSchemaService.update(schema_id, schema_data)


@router.patch(
    "/client-schemas/{schema_id}/activate",
    response_model=APIResponse,
    summary="Activate schema version",
    description="Sets a specific version as active. Use when: 'activate version', 'make version active', 'switch to version'.",
)
async def activate_schema_version(schema_id: str):
    """
    Activate a specific version of a schema
    
    - Deactivates all other versions of the same schema
    - Sets this version as the active one
    """
    return await ClientSchemaService.activate_version(schema_id)


@router.delete(
    "/client-schemas/{schema_id}",
    response_model=APIResponse,
    summary="Delete schema",
    description="Deletes a schema permanently. Use when: 'delete schema', 'remove schema version'.",
)
async def delete_client_schema(schema_id: str):
    """Delete a client schema"""
    return await ClientSchemaService.delete(schema_id)