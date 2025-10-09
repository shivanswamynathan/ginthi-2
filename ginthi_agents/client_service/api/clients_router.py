from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.client_models import Clients
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import ClientCreate, ClientUpdate, ClientResponse
import logging
from datetime import datetime, timezone
from uuid import UUID

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/clients/create", response_model=ClientResponse)
async def create_client(client_data: ClientCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if ClientName already exists
        result = await db.execute(select(Clients).where(Clients.ClientName == client_data.ClientName))
        existing_name = result.scalar_one_or_none()
        
        if existing_name:
            logger.warning(f"Duplicate client name: {client_data.ClientName}")
            raise HTTPException(
                status_code=400,
                detail=f"Client with name '{client_data.ClientName}' already exists"
            )

        # Create new client (UUID will be auto-generated)
        new_client = Clients(**client_data.model_dump(exclude_unset=True))
        
        db.add(new_client)
        await db.commit()
        await db.refresh(new_client)
        
        logger.info(f"Client created successfully: {new_client.ClientName}")
        return new_client

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Clients).where(Clients.ClientID == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {client_id} not found"
            )
        
        logger.info(f"Client retrieved: {client.ClientName}")
        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clients", response_model=list[ClientResponse])
async def get_all_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Clients).offset(skip).limit(limit))
        clients = result.scalars().all()
        
        logger.info(f"Retrieved {len(clients)} clients")
        return list(clients)

    except Exception as e:
        logger.error(f"Error retrieving clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: UUID, client_data: ClientUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Clients).where(Clients.ClientID == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {client_id} not found"
            )

        # Update fields
        for key, value in client_data.model_dump(exclude_unset=True).items():
            setattr(client, key, value)
        
        client.UpdatedAt = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(client)
        
        logger.info(f"Client updated: {client.ClientName}")
        return client

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/clients/{client_id}")
async def delete_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Clients).where(Clients.ClientID == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {client_id} not found"
            )

        await db.delete(client)
        await db.commit()
        
        logger.info(f"Client deleted: {client.ClientName}")
        return {"message": f"Client {client_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")