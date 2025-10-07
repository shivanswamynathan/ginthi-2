from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.client_models import ClientEntity, Clients
from client_service.db.mongo_db import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== CLIENT ENTITY CRUD ====================

@router.post("/entities/create", response_model=ClientEntity)
async def create_entity(entity: ClientEntity, db=Depends(get_db)):
    try:
        # Check if EntityID already exists
        existing = await ClientEntity.find_one(ClientEntity.EntityID == entity.EntityID)
        if existing:
            logger.warning(f"Duplicate entity creation attempt: EntityID {entity.EntityID}")
            raise HTTPException(
                status_code=400,
                detail=f"Entity with EntityID {entity.EntityID} already exists"
            )

        # Verify ClientID exists
        client = await Clients.find_one(Clients.ClientID == entity.ClientID)
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {entity.ClientID} not found"
            )

        # Insert the entity
        await entity.insert()
        logger.info(f"Entity created successfully: {entity.EntityName}")
        
        return entity

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/entities/{entity_id}", response_model=ClientEntity)
async def get_entity(entity_id: int, db=Depends(get_db)):
    try:
        entity = await ClientEntity.find_one(
            ClientEntity.EntityID == entity_id,
            fetch_links=True
        )
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


@router.get("/entities", response_model=list[ClientEntity])
async def get_all_entities(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        entities = await ClientEntity.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(entities)} entities")
        return entities

    except Exception as e:
        logger.error(f"Error retrieving entities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/entities/client/{client_id}", response_model=list[ClientEntity])
async def get_entities_by_client(client_id: int, db=Depends(get_db)):
    try:
        entities = await ClientEntity.find(
            ClientEntity.ClientID == client_id
        ).to_list()
        
        if not entities:
            logger.info(f"No entities found for client {client_id}")
            return []
        
        logger.info(f"Retrieved {len(entities)} entities for client {client_id}")
        return entities

    except Exception as e:
        logger.error(f"Error retrieving client entities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/entities/{entity_id}", response_model=ClientEntity)
async def update_entity(entity_id: int, entity_data: ClientEntity, db=Depends(get_db)):
    try:
        entity = await ClientEntity.find_one(ClientEntity.EntityID == entity_id)
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with ID {entity_id} not found"
            )

        # Update fields
        entity.ClientID = entity_data.ClientID
        entity.GSTID = entity_data.GSTID
        entity.CompanyPan = entity_data.CompanyPan
        entity.EntityName = entity_data.EntityName
        entity.TAN = entity_data.TAN
        entity.ParentClientID = entity_data.ParentClientID

        await entity.save()
        logger.info(f"Entity updated: {entity.EntityName}")
        
        return entity

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/entities/{entity_id}")
async def delete_entity(entity_id: int, db=Depends(get_db)):
    try:
        entity = await ClientEntity.find_one(ClientEntity.EntityID == entity_id)
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity with ID {entity_id} not found"
            )

        await entity.delete()
        logger.info(f"Entity deleted: {entity.EntityName}")
        
        return {"message": f"Entity {entity_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")