from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.client_models import ClientEntity, Clients
from client_service.db.postgres_db import get_db
from client_service.schemas.pydantic_schemas import ClientEntityCreate, ClientEntityUpdate, ClientEntityResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/entities/create", response_model=ClientEntityResponse)
async def create_entity(entity_data: ClientEntityCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if EntityID already exists
        result = await db.execute(select(ClientEntity).where(ClientEntity.EntityID == entity_data.EntityID))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.warning(f"Duplicate entity creation attempt: EntityID {entity_data.EntityID}")
            raise HTTPException(
                status_code=400,
                detail=f"Entity with EntityID {entity_data.EntityID} already exists"
            )

        # Verify ClientID exists
        result = await db.execute(select(Clients).where(Clients.ClientID == entity_data.ClientID))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {entity_data.ClientID} not found"
            )

        # Create new entity
        new_entity = ClientEntity(**entity_data.model_dump())
        
        db.add(new_entity)
        await db.commit()
        await db.refresh(new_entity)
        
        logger.info(f"Entity created successfully: {new_entity.EntityName}")
        return new_entity

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/entities/{entity_id}", response_model=ClientEntityResponse)
async def get_entity(entity_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ClientEntity).where(ClientEntity.EntityID == entity_id))
        entity = result.scalar_one_or_none()
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with ID {entity_id} not found"
            )
        
        logger.info(f"Entity retrieved: {entity.EntityName}")
        return entity

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/entities", response_model=list[ClientEntityResponse])
async def get_all_entities(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ClientEntity).offset(skip).limit(limit))
        entities = result.scalars().all()
        
        logger.info(f"Retrieved {len(entities)} entities")
        return list(entities)

    except Exception as e:
        logger.error(f"Error retrieving entities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/entities/client/{client_id}", response_model=list[ClientEntityResponse])
async def get_entities_by_client(client_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ClientEntity).where(ClientEntity.ClientID == client_id))
        entities = result.scalars().all()
        
        if not entities:
            logger.info(f"No entities found for client {client_id}")
            return []
        
        logger.info(f"Retrieved {len(entities)} entities for client {client_id}")
        return list(entities)

    except Exception as e:
        logger.error(f"Error retrieving client entities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/entities/{entity_id}", response_model=ClientEntityResponse)
async def update_entity(entity_id: int, entity_data: ClientEntityUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ClientEntity).where(ClientEntity.EntityID == entity_id))
        entity = result.scalar_one_or_none()
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with ID {entity_id} not found"
            )

        # Update fields
        for key, value in entity_data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)

        await db.commit()
        await db.refresh(entity)
        
        logger.info(f"Entity updated: {entity.EntityName}")
        return entity

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/entities/{entity_id}")
async def delete_entity(entity_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ClientEntity).where(ClientEntity.EntityID == entity_id))
        entity = result.scalar_one_or_none()
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with ID {entity_id} not found"
            )

        await db.delete(entity)
        await db.commit()
        
        logger.info(f"Entity deleted: {entity.EntityName}")
        return {"message": f"Entity {entity_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")