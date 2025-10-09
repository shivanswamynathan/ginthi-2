from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.clients_service import ClientService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse
)
from uuid import UUID

router = APIRouter()


@router.post("/clients/create", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new client"""
    return await ClientService.create(client_data, db)


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a client by ID"""
    return await ClientService.get_by_id(client_id, db)


@router.get("/clients", response_model=list[ClientResponse])
async def get_all_clients(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all clients with pagination"""
    return await ClientService.get_all(skip, limit, db)


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a client"""
    return await ClientService.update(client_id, client_data, db)


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a client"""
    return await ClientService.delete(client_id, db)