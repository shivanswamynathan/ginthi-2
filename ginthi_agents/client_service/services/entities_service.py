from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from client_service.schemas.client_db.client_models import ClientEntity, Clients
from client_service.schemas.pydantic_schemas import ClientEntityCreate, ClientEntityUpdate, ClientEntityResponse
from client_service.api.constants.messages import EntityMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
from datetime import datetime, timezone
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class EntityService:
    """Service class for Entity business logic"""
    
    @staticmethod
    async def create(entity_data: ClientEntityCreate, db: AsyncSession):
        """Create a new entity"""
        try:
            # Verify ClientID exists
            result = await db.execute(
                select(Clients).where(Clients.client_id == entity_data.client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=EntityMessages.CLIENT_NOT_FOUND.format(id=entity_data.client_id)
                )

            # Create new entity (UUID will be auto-generated)
            new_entity = ClientEntity(**entity_data.model_dump(exclude_unset=True))
            
            db.add(new_entity)
            await db.commit()
            await db.refresh(new_entity)
            
            logger.info(EntityMessages.CREATED_SUCCESS.format(name=new_entity.entity_name))
            return APIResponse(
                success=True,
                message=EntityMessages.CREATED_SUCCESS.format(name=new_entity.entity_name),
                data=ClientEntityResponse.model_validate(new_entity).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(EntityMessages.CREATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=EntityMessages.CREATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_id(entity_id: UUID, db: AsyncSession):
        """Get an entity by ID"""
        try:
            result = await db.execute(
                select(ClientEntity).where(ClientEntity.entity_id == entity_id)
            )
            entity = result.scalar_one_or_none()
            
            if not entity:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=EntityMessages.NOT_FOUND.format(id=entity_id)
                )
            
            logger.info(EntityMessages.RETRIEVED_SUCCESS.format(name=entity.entity_name))
            return APIResponse(
                success=True,   
                message=EntityMessages.RETRIEVED_SUCCESS.format(name=entity.entity_name),
                data=ClientEntityResponse.model_validate(entity).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(EntityMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=EntityMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_all(skip: int, limit: int, db: AsyncSession):
        """Get all entities with pagination"""
        try:
            result = await db.execute(
                select(ClientEntity).offset(skip).limit(limit)
            )
            entities = result.scalars().all()
            
            logger.info(EntityMessages.RETRIEVED_ALL_SUCCESS.format(count=len(entities)))
            return APIResponse(
                success=True,
                message=EntityMessages.RETRIEVED_ALL_SUCCESS.format(count=len(entities)),
                data=[ClientEntityResponse.model_validate(entity).model_dump() for entity in entities]
            )


        except Exception as e:
            logger.error(EntityMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=EntityMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )

    @staticmethod
    async def get_by_client_id(client_id: UUID, db: AsyncSession):
        """Get all entities by client ID"""
        try:
            result = await db.execute(
                select(ClientEntity).where(ClientEntity.client_id == client_id)
            )
            entities = result.scalars().all()
            
            if not entities:
                logger.info(EntityMessages.NO_ENTITIES_FOR_CLIENT.format(id=client_id))
                return []
            
            logger.info(EntityMessages.RETRIEVED_BY_CLIENT_SUCCESS.format(count=len(entities), id=client_id))
            return APIResponse(
                success=True,   
                message=EntityMessages.RETRIEVED_BY_CLIENT_SUCCESS.format(count=len(entities), id=client_id),
                data=[ClientEntityResponse.model_validate(entity).model_dump() for entity in entities]
            )

        except Exception as e:
            logger.error(EntityMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=EntityMessages.RETRIEVE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def update(entity_id: UUID, entity_data: ClientEntityUpdate, db: AsyncSession):
        """Update an entity"""
        try:
            result = await db.execute(
                select(ClientEntity).where(ClientEntity.entity_id == entity_id)
            )
            entity = result.scalar_one_or_none()
            
            if not entity:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=EntityMessages.NOT_FOUND.format(id=entity_id)
                )

            # Update fields
            for key, value in entity_data.model_dump(exclude_unset=True).items():
                setattr(entity, key, value)
            
            entity.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(entity)
            
            logger.info(EntityMessages.UPDATED_SUCCESS.format(name=entity.entity_name))
            return APIResponse(
                success=True,
                message=EntityMessages.UPDATED_SUCCESS.format(name=entity.entity_name),
                data=ClientEntityResponse.model_validate(entity).model_dump()
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(EntityMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=EntityMessages.UPDATE_ERROR.format(error=str(e))
            )

    @staticmethod
    async def delete(entity_id: UUID, db: AsyncSession):
        """Delete an entity"""
        try:
            result = await db.execute(
                select(ClientEntity).where(ClientEntity.entity_id == entity_id)
            )
            entity = result.scalar_one_or_none()
            
            if not entity:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=EntityMessages.NOT_FOUND.format(id=entity_id)
                )

            await db.delete(entity)
            await db.commit()
            
            logger.info(EntityMessages.DELETED_SUCCESS.format(id=entity_id))
            return APIResponse(
                success=True,
                message=EntityMessages.DELETED_SUCCESS.format(id=entity_id),
                data=None
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(EntityMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=EntityMessages.DELETE_ERROR.format(error=str(e))
            )