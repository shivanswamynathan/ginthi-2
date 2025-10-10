from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.entities_service import EntityService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    ClientEntityCreate,
    ClientEntityUpdate,
    ClientEntityResponse
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/entities/create",
    response_model=ClientEntityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create client entity",
    description="Creates a new entity (branch/subsidiary). Use when: 'create entity', 'add branch', 'register subsidiary'.",
)
async def create_entity(
    entity_data: ClientEntityCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new entity"""
    return await EntityService.create(entity_data, db)


@router.get(
    "/entities/{entity_id}",
    response_model=ClientEntityResponse,
    summary="Get entity by ID",
    description="Retrieves entity details by UUID. Use when: 'get entity', 'show entity', 'find branch'.",
)
async def get_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get an entity by ID"""
    return await EntityService.get_by_id(entity_id, db)


@router.get(
    "/entities",
    response_model=list[ClientEntityResponse],
    summary="List all entities",
    description="Get all entities with pagination. Use when: 'list entities', 'show all branches'.",
)
async def get_all_entities(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all entities with pagination"""
    return await EntityService.get_all(skip, limit, db)


@router.get(
    "/entities/client/{client_id}",
    response_model=list[ClientEntityResponse],
    summary="Get entities by client",
    description="Get all entities for a specific client. Use when: 'show client branches', 'list entities for client'.",
)
async def get_entities_by_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all entities by client ID"""
    return await EntityService.get_by_client_id(client_id, db)


@router.put(
    "/entities/{entity_id}",
    response_model=ClientEntityResponse,
    summary="Update entity",
    description="Updates entity information (name, GST, PAN). Use when: 'update entity', 'modify branch'.",
)
async def update_entity(
    entity_id: UUID,
    entity_data: ClientEntityUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update an entity"""
    return await EntityService.update(entity_id, entity_data, db)


@router.delete(
    "/entities/{entity_id}",
    summary="Delete entity",
    description="Deletes an entity permanently. Use when: 'delete entity', 'remove branch'.",
)
async def delete_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete an entity"""
    return await EntityService.delete(entity_id, db)