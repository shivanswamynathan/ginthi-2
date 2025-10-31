from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.client_models import CentralClients
from client_service.schemas.pydantic_schemas import CentralClientCreate, CentralClientUpdate
from client_service.api.constants.messages import CentralClientMessages
from client_service.schemas.pydantic_schemas import CentralClientResponse
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse

import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class CentralClientService:
    """Service class for Central Client business logic"""
    
    @staticmethod
    async def create(central_client_data: CentralClientCreate, db: AsyncSession):
        """Create a new central client"""
        try:
            # Create new central client (UUID will be auto-generated)
            new_central_client = CentralClients(**central_client_data.model_dump(exclude_unset=True))
            
            db.add(new_central_client)
            await db.commit()
            await db.refresh(new_central_client)
            
            logger.info(CentralClientMessages.CREATED_SUCCESS.format(name=new_central_client.name))
            return APIResponse(
                success=True,
                message=CentralClientMessages.CREATED_SUCCESS.format(name=new_central_client.name),
                data=CentralClientResponse.model_validate(new_central_client).model_dump()
            )

        except Exception as e:
            await db.rollback()
            logger.error(CentralClientMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=CentralClientMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(client_id: UUID, db: AsyncSession):
        """Get a central client by ID"""
        try:
            result = await db.execute(
                select(CentralClients).where(CentralClients.client_id == client_id)
            )
            central_client = result.scalar_one_or_none()
            
            if not central_client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=CentralClientMessages.NOT_FOUND.format(id=client_id)
                )
            
            logger.info(CentralClientMessages.RETRIEVED_SUCCESS.format(name=central_client.name))
            return APIResponse(
                success=True,
                message=CentralClientMessages.RETRIEVED_SUCCESS.format(name=central_client.name),
                data=CentralClientResponse.model_validate(central_client).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(CentralClientMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=CentralClientMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all central clients with pagination"""
        try:
            result = await db.execute(
                select(CentralClients).offset(skip).limit(limit)
            )
            central_clients = result.scalars().all()
            
            logger.info(CentralClientMessages.RETRIEVED_ALL_SUCCESS.format(count=len(central_clients)))
            return APIResponse(
                success=True,
                message=CentralClientMessages.RETRIEVED_ALL_SUCCESS.format(count=len(central_clients)),
                data=[CentralClientResponse.model_validate(client).model_dump() for client in central_clients]
            )

        except Exception as e:
            logger.error(CentralClientMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=CentralClientMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(client_id: UUID, central_client_data: CentralClientUpdate, db: AsyncSession):
        """Update a central client"""
        try:
            result = await db.execute(
                select(CentralClients).where(CentralClients.client_id == client_id)
            )
            central_client = result.scalar_one_or_none()
            
            if not central_client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=CentralClientMessages.NOT_FOUND.format(id=client_id)
                )

            # Update fields
            for key, value in central_client_data.model_dump(exclude_unset=True).items():
                setattr(central_client, key, value)

            await db.commit()
            await db.refresh(central_client)
            
            logger.info(CentralClientMessages.UPDATED_SUCCESS.format(name=central_client.name))
            return APIResponse(
                success=True,
                message=CentralClientMessages.UPDATED_SUCCESS.format(name=central_client.name),
                data=CentralClientResponse.model_validate(central_client).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(CentralClientMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=CentralClientMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(client_id: UUID, db: AsyncSession):
        """Delete a central client"""
        try:
            result = await db.execute(
                select(CentralClients).where(CentralClients.client_id == client_id)
            )
            central_client = result.scalar_one_or_none()
            
            if not central_client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=CentralClientMessages.NOT_FOUND.format(id=client_id)
                )

            await db.delete(central_client)
            await db.commit()
            
            logger.info(CentralClientMessages.DELETED_SUCCESS.format(id=client_id))
            return APIResponse(
                success=True,
                message=CentralClientMessages.DELETED_SUCCESS.format(id=client_id),
                data=None
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(CentralClientMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=CentralClientMessages.DELETE_ERROR.format(error=str(e))
            )