from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.client_models import CentralClients
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import CentralClientCreate, CentralClientUpdate, CentralClientResponse
import logging
from uuid import UUID

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/central-clients/create", response_model=CentralClientResponse)
async def create_central_client(central_client_data: CentralClientCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Create new central client (UUID will be auto-generated)
        new_central_client = CentralClients(**central_client_data.model_dump(exclude_unset=True))
        
        db.add(new_central_client)
        await db.commit()
        await db.refresh(new_central_client)
        
        logger.info(f"Central client created successfully: {new_central_client.Name}")
        return new_central_client

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating central client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/central-clients/{client_id}", response_model=CentralClientResponse)
async def get_central_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CentralClients).where(CentralClients.ClientID == client_id))
        central_client = result.scalar_one_or_none()
        
        if not central_client:
            raise HTTPException(
                status_code=404,
                detail=f"Central client with ID {client_id} not found"
            )
        
        logger.info(f"Central client retrieved: {central_client.Name}")
        return central_client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving central client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/central-clients", response_model=list[CentralClientResponse])
async def get_all_central_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CentralClients).offset(skip).limit(limit))
        central_clients = result.scalars().all()
        
        logger.info(f"Retrieved {len(central_clients)} central clients")
        return list(central_clients)

    except Exception as e:
        logger.error(f"Error retrieving central clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/central-clients/{client_id}", response_model=CentralClientResponse)
async def update_central_client(client_id: UUID, central_client_data: CentralClientUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CentralClients).where(CentralClients.ClientID == client_id))
        central_client = result.scalar_one_or_none()
        
        if not central_client:
            raise HTTPException(
                status_code=404,
                detail=f"Central client with ID {client_id} not found"
            )

        # Update fields
        for key, value in central_client_data.model_dump(exclude_unset=True).items():
            setattr(central_client, key, value)

        await db.commit()
        await db.refresh(central_client)
        
        logger.info(f"Central client updated: {central_client.Name}")
        return central_client

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating central client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/central-clients/{client_id}")
async def delete_central_client(client_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CentralClients).where(CentralClients.ClientID == client_id))
        central_client = result.scalar_one_or_none()
        
        if not central_client:
            raise HTTPException(
                status_code=404,
                detail=f"Central client with ID {client_id} not found"
            )

        await db.delete(central_client)
        await db.commit()
        
        logger.info(f"Central client deleted: {central_client.Name}")
        return {"message": f"Central client {client_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting central client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")