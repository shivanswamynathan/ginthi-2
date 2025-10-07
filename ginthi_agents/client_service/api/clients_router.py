from fastapi import APIRouter, HTTPException, Depends
from client_service.schemas.client_db.client_models import Clients, CentralClients, ClientEntity
from client_service.db.mongo_db import get_db
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# ==================== CLIENT CRUD ====================


@router.post("/clients/create", response_model=Clients)
async def create_client(client: Clients, db=Depends(get_db)):
    try:
        # Check if ClientID already exists
        existing = await Clients.find_one(Clients.ClientID == client.ClientID)
        if existing:
            logger.warning(f"Duplicate client creation attempt: ClientID {client.ClientID}")
            raise HTTPException(
                status_code=400,
                detail=f"Client with ClientID {client.ClientID} already exists"
            )

        # Check if ClientName already exists
        existing_name = await Clients.find_one(Clients.ClientName == client.ClientName)
        if existing_name:
            logger.warning(f"Duplicate client name: {client.ClientName}")
            raise HTTPException(
                status_code=400,
                detail=f"Client with name '{client.ClientName}' already exists"
            )

        # Insert the client
        await client.insert()
        logger.info(f"Client created successfully: {client.ClientName}")
        
        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clients/{client_id}", response_model=Clients)
async def get_client(client_id: int, db=Depends(get_db)):
    try:
        client = await Clients.find_one(Clients.ClientID == client_id, fetch_links=True)
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


@router.get("/clients", response_model=list[Clients])
async def get_all_clients(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    try:
        clients = await Clients.find_all().skip(skip).limit(limit).to_list()
        logger.info(f"Retrieved {len(clients)} clients")
        return clients

    except Exception as e:
        logger.error(f"Error retrieving clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clients/{client_id}", response_model=Clients)
async def update_client(client_id: int, client_data: Clients, db=Depends(get_db)):
    try:
        # Find existing client
        client = await Clients.find_one(Clients.ClientID == client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {client_id} not found"
            )

        # Update fields
        client.ClientName = client_data.ClientName
        client.CentralClientID = client_data.CentralClientID
        client.CentralAPIKey = client_data.CentralAPIKey
        client.UpdatedAt = datetime.utcnow()

        # Save changes
        await client.save()
        logger.info(f"Client updated: {client.ClientName}")
        
        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/clients/{client_id}")
async def delete_client(client_id: int, db=Depends(get_db)):
    try:
        client = await Clients.find_one(Clients.ClientID == client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {client_id} not found"
            )

        await client.delete()
        logger.info(f"Client deleted: {client.ClientName}")
        
        return {"message": f"Client {client_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")