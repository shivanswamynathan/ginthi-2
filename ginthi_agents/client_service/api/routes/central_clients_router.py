from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from client_service.services.central_client_service import CentralClientService
from client_service.api.dependencies import get_database_session
from client_service.schemas.pydantic_schemas import (
    CentralClientCreate, 
    CentralClientUpdate, 
    CentralClientResponse
)
from uuid import UUID

router = APIRouter()


@router.post("/central-clients/create", response_model=CentralClientResponse)
async def create_central_client(
    central_client_data: CentralClientCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """Create a new central client"""
    return await CentralClientService.create(central_client_data, db)


@router.get("/central-clients/{client_id}", response_model=CentralClientResponse)
async def get_central_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Get a central client by ID"""
    return await CentralClientService.get_by_id(client_id, db)


@router.get("/central-clients", response_model=list[CentralClientResponse])
async def get_all_central_clients(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """Get all central clients with pagination"""
    return await CentralClientService.get_all(skip, limit, db)


@router.put("/central-clients/{client_id}", response_model=CentralClientResponse)
async def update_central_client(
    client_id: UUID,
    central_client_data: CentralClientUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """Update a central client"""
    return await CentralClientService.update(client_id, central_client_data, db)


@router.delete("/central-clients/{client_id}")
async def delete_central_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_database_session)
):
    """Delete a central client"""
    return await CentralClientService.delete(client_id, db)