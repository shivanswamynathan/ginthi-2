from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.client_models import CentralClients
from client_service.db.mongo_db import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== CENTRAL CLIENTS CRUD ====================

@router.post("/central-clients/create", response_model=CentralClients)
async def create_central_client(central_client: CentralClients, db=Depends(get_db)):
    try:
        # Check if ClientID already exists
        existing = await CentralClients.find_one(
            CentralClients.ClientID == central_client.ClientID
        )
        if existing:
            logger.warning(f"Duplicate central client creation attempt: ClientID {central_client.ClientID}")
            raise HTTPException(
                status_code=400,
                detail=f"Central client with ClientID {central_client.ClientID} already exists"
            )

        # Insert the central client
        await central_client.insert()
        logger.info(f"Central client created successfully: {central_client.Name}")
        
        return central_client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating central client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/central-clients/{client_id}", response_model=CentralClients)
async def get_central_client(client_id: int, db=Depends(get_db)):
    try:
        central_client = await CentralClients.find_one(
            CentralClients.ClientID == client_id
        )
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


@router.get("/central-clients", response_model=list[CentralClients])
async def get_all_central_clients(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        central_clients = await CentralClients.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(central_clients)} central clients")
        return central_clients

    except Exception as e:
        logger.error(f"Error retrieving central clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/central-clients/{client_id}", response_model=CentralClients)
async def update_central_client(client_id: int, central_client_data: CentralClients, db=Depends(get_db)):
    try:
        central_client = await CentralClients.find_one(
            CentralClients.ClientID == client_id
        )
        if not central_client:
            raise HTTPException(
                status_code=404,
                detail=f"Central client with ID {client_id} not found"
            )

        # Update fields
        central_client.Name = central_client_data.Name

        await central_client.save()
        logger.info(f"Central client updated: {central_client.Name}")
        
        return central_client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating central client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/central-clients/{client_id}")
async def delete_central_client(client_id: int, db=Depends(get_db)):
    try:
        central_client = await CentralClients.find_one(
            CentralClients.ClientID == client_id
        )
        if not central_client:
            raise HTTPException(
                status_code=404,
                detail=f"Central client with ID {client_id} not found"
            )

        await central_client.delete()
        logger.info(f"Central client deleted: {central_client.Name}")
        
        return {"message": f"Central client {client_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting central client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")