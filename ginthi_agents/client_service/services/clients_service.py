from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.client_models import Clients
from client_service.schemas.pydantic_schemas import ClientCreate, ClientUpdate
from client_service.api.constants.messages import ClientMessages
from client_service.api.constants.status_codes import StatusCode
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class ClientService:
    """Service class for Client business logic"""
    
    @staticmethod
    async def create(client_data: ClientCreate, db: AsyncSession):
        """Create a new client"""
        try:
            # Check if ClientName already exists
            result = await db.execute(
                select(Clients).where(Clients.client_name == client_data.client_name)
            )
            existing_name = result.scalar_one_or_none()
            
            if existing_name:
                logger.warning(ClientMessages.DUPLICATE_NAME.format(name=client_data.client_name))
                raise HTTPException(
                    status_code=StatusCode.CONFLICT,
                    detail=ClientMessages.DUPLICATE_NAME.format(name=client_data.client_name)
                )

            # Create new client (UUID will be auto-generated)
            new_client = Clients(**client_data.model_dump(exclude_unset=True))
            
            db.add(new_client)
            await db.commit()
            await db.refresh(new_client)
            
            logger.info(ClientMessages.CREATED_SUCCESS.format(name=new_client.client_name))
            return new_client

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(ClientMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(client_id: UUID, db: AsyncSession):
        """Get a client by ID"""
        try:
            result = await db.execute(
                select(Clients).where(Clients.client_id == client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientMessages.NOT_FOUND.format(id=client_id)
                )
            
            logger.info(ClientMessages.RETRIEVED_SUCCESS.format(name=client.client_name))
            return client

        except HTTPException:
            raise
        except Exception as e:
            logger.error(ClientMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all clients with pagination"""
        try:
            result = await db.execute(
                select(Clients).offset(skip).limit(limit)
            )
            clients = result.scalars().all()
            
            logger.info(ClientMessages.RETRIEVED_ALL_SUCCESS.format(count=len(clients)))
            return list(clients)

        except Exception as e:
            logger.error(ClientMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(client_id: UUID, client_data: ClientUpdate, db: AsyncSession):
        """Update a client"""
        try:
            result = await db.execute(
                select(Clients).where(Clients.client_id == client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientMessages.NOT_FOUND.format(id=client_id)
                )

            # Update fields
            for key, value in client_data.model_dump(exclude_unset=True).items():
                setattr(client, key, value)
            
            client.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(client)
            
            logger.info(ClientMessages.UPDATED_SUCCESS.format(name=client.client_name))
            return client

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(ClientMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(client_id: UUID, db: AsyncSession):
        """Delete a client"""
        try:
            result = await db.execute(
                select(Clients).where(Clients.client_id == client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientMessages.NOT_FOUND.format(id=client_id)
                )

            await db.delete(client)
            await db.commit()
            
            logger.info(ClientMessages.DELETED_SUCCESS.format(id=client_id))
            return {"message": ClientMessages.DELETED_SUCCESS.format(id=client_id)}

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(ClientMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientMessages.DELETE_ERROR.format(error=str(e))
            )