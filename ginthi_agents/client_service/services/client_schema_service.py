from fastapi import HTTPException
from beanie import PydanticObjectId
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select  
from client_service.schemas.mongo_schemas.client_schema_model import ClientSchema, SchemaField
from client_service.schemas.client_db.client_models import Clients  
from client_service.schemas.pydantic_schemas import (
    ClientSchemaCreate, 
    ClientSchemaUpdate, 
    ClientSchemaResponse,
    SchemaFieldCreate
)
from client_service.api.constants.messages import ClientSchemaMessages
from client_service.api.constants.status_codes import StatusCode
from client_service.schemas.base_response import APIResponse
from datetime import datetime, timezone
from typing import Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class ClientSchemaService:
    """Service class for Client Schema business logic"""
    
    @staticmethod
    async def create(schema_data: ClientSchemaCreate, db: AsyncSession):  # ← ADDED db parameter
        """
        Create a new client schema
        - Validates client_id exists in PostgreSQL
        - Auto-generates version if not provided
        - Deactivates other versions if is_active=True
        """
        try:
            # Validate client_id format first
            try:
                UUID(schema_data.client_id)
            except ValueError:
                raise HTTPException(
                    status_code=StatusCode.BAD_REQUEST,
                    detail=f"Invalid client_id format. Must be a valid UUID, got: {schema_data.client_id}"
                )
            
            # ============================================================
            # CHECK IF CLIENT EXISTS IN POSTGRESQL
            # ============================================================
            result = await db.execute(
                select(Clients).where(Clients.client_id == schema_data.client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=f"Client with ID {schema_data.client_id} not found in database"
                )
            # ============================================================
            
            # Check if schema with same name exists for this client
            existing_schemas = await ClientSchema.find(
                ClientSchema.client_id == schema_data.client_id,
                ClientSchema.schema_name == schema_data.schema_name
            ).sort(-ClientSchema.version).to_list()
            
            # Determine version number
            if schema_data.version:
                version = schema_data.version
                # Check if this version already exists
                version_exists = any(s.version == version for s in existing_schemas)
                if version_exists:
                    raise HTTPException(
                        status_code=StatusCode.CONFLICT,
                        detail=ClientSchemaMessages.DUPLICATE_SCHEMA.format(
                            name=schema_data.schema_name,
                            version=version,
                            client_id=schema_data.client_id
                        )
                    )
            else:
                # Auto-generate version (max + 1)
                version = max([s.version for s in existing_schemas], default=0) + 1
            
            # If this version should be active, deactivate all other versions
            if schema_data.is_active:
                for schema in existing_schemas:
                    if schema.is_active:
                        schema.is_active = False
                        schema.updated_at = datetime.now(timezone.utc)
                        await schema.save()
            
            # Convert SchemaFieldCreate to dict (not SchemaField objects)
            fields = [field.model_dump() for field in schema_data.fields]
            
            # Create new schema document
            new_schema = ClientSchema(
                client_id=schema_data.client_id,
                schema_name=schema_data.schema_name,
                version=version,
                is_active=schema_data.is_active,
                description=schema_data.description,
                fields=fields,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            await new_schema.insert()
            
            logger.info(ClientSchemaMessages.CREATED_SUCCESS.format(
                name=new_schema.schema_name,
                version=new_schema.version
            ))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.CREATED_SUCCESS.format(
                    name=new_schema.schema_name,
                    version=new_schema.version
                ),
                data=ClientSchemaResponse(
                    _id=str(new_schema.id),
                    client_id=new_schema.client_id,
                    schema_name=new_schema.schema_name,
                    version=new_schema.version,
                    is_active=new_schema.is_active,
                    description=new_schema.description,
                    fields=new_schema.fields,
                    created_at=new_schema.created_at,
                    updated_at=new_schema.updated_at
                ).model_dump(by_alias=True)
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating client schema: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=f"Error creating client schema: {str(e)}"
            )
    
    @staticmethod
    async def get_by_id(schema_id: str):
        """Get a client schema by MongoDB ObjectId"""
        try:
            schema = await ClientSchema.get(PydanticObjectId(schema_id))
            
            if not schema:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientSchemaMessages.NOT_FOUND.format(id=schema_id)
                )
            
            logger.info(ClientSchemaMessages.RETRIEVED_SUCCESS.format(
                name=schema.schema_name,
                version=schema.version
            ))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.RETRIEVED_SUCCESS.format(
                    name=schema.schema_name,
                    version=schema.version
                ),
                data=ClientSchemaResponse(
                    _id=str(schema.id),
                    client_id=schema.client_id,
                    schema_name=schema.schema_name,
                    version=schema.version,
                    is_active=schema.is_active,
                    description=schema.description,
                    fields=schema.fields,
                    created_at=schema.created_at,
                    updated_at=schema.updated_at
                ).model_dump(by_alias=True)
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e))
            )
    
    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100):
        """Get all client schemas with pagination"""
        try:
            schemas = await ClientSchema.find_all().skip(skip).limit(limit).to_list()
            
            logger.info(ClientSchemaMessages.RETRIEVED_ALL_SUCCESS.format(count=len(schemas)))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.RETRIEVED_ALL_SUCCESS.format(count=len(schemas)),
                data=[
                    ClientSchemaResponse(
                        _id=str(schema.id),
                        client_id=schema.client_id,
                        schema_name=schema.schema_name,
                        version=schema.version,
                        is_active=schema.is_active,
                        description=schema.description,
                        fields=schema.fields,
                        created_at=schema.created_at,
                        updated_at=schema.updated_at
                    ).model_dump(by_alias=True)
                    for schema in schemas
                ]
            )
        
        except Exception as e:
            logger.error(ClientSchemaMessages.RETRIEVE_ALL_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.RETRIEVE_ALL_ERROR.format(error=str(e))
            )
    
    @staticmethod
    async def get_by_client_id(client_id: str):
        """Get all schemas for a specific client"""
        try:
            schemas = await ClientSchema.find(
                ClientSchema.client_id == client_id
            ).to_list()
            
            if not schemas:
                logger.info(ClientSchemaMessages.NO_SCHEMAS_FOR_CLIENT.format(id=client_id))
                return APIResponse(
                    success=True,
                    message=ClientSchemaMessages.NO_SCHEMAS_FOR_CLIENT.format(id=client_id),
                    data=[]
                )
            
            logger.info(ClientSchemaMessages.RETRIEVED_BY_CLIENT_SUCCESS.format(
                count=len(schemas),
                id=client_id
            ))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.RETRIEVED_BY_CLIENT_SUCCESS.format(
                    count=len(schemas),
                    id=client_id
                ),
                data=[
                    ClientSchemaResponse(
                        _id=str(schema.id),
                        client_id=schema.client_id,
                        schema_name=schema.schema_name,
                        version=schema.version,
                        is_active=schema.is_active,
                        description=schema.description,
                        fields=schema.fields,
                        created_at=schema.created_at,
                        updated_at=schema.updated_at
                    ).model_dump(by_alias=True)
                    for schema in schemas
                ]
            )
        
        except Exception as e:
            logger.error(ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e))
            )
    
    @staticmethod
    async def get_by_client_and_name(client_id: str, schema_name: str):
        """Get all versions of a specific schema for a client"""
        try:
            schemas = await ClientSchema.find(
                ClientSchema.client_id == client_id,
                ClientSchema.schema_name == schema_name
            ).sort(-ClientSchema.version).to_list()
            
            if not schemas:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientSchemaMessages.NOT_FOUND_BY_NAME.format(
                        name=schema_name,
                        client_id=client_id
                    )
                )
            
            logger.info(ClientSchemaMessages.RETRIEVED_BY_CLIENT_SUCCESS.format(
                count=len(schemas),
                id=client_id
            ))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.RETRIEVED_BY_CLIENT_SUCCESS.format(
                    count=len(schemas),
                    id=client_id
                ),
                data=[
                    ClientSchemaResponse(
                        _id=str(schema.id),
                        client_id=schema.client_id,
                        schema_name=schema.schema_name,
                        version=schema.version,
                        is_active=schema.is_active,
                        description=schema.description,
                        fields=schema.fields,
                        created_at=schema.created_at,
                        updated_at=schema.updated_at
                    ).model_dump(by_alias=True)
                    for schema in schemas
                ]
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e))
            )
    
    @staticmethod
    async def get_active_schema(client_id: str, schema_name: str):
        """Get the active version of a schema"""
        try:
            schema = await ClientSchema.find_one(
                ClientSchema.client_id == client_id,
                ClientSchema.schema_name == schema_name,
                ClientSchema.is_active == True
            )
            
            if not schema:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientSchemaMessages.NO_ACTIVE_VERSION.format(
                        name=schema_name,
                        client_id=client_id
                    )
                )
            
            logger.info(ClientSchemaMessages.RETRIEVED_ACTIVE_SUCCESS.format(
                name=schema.schema_name,
                version=schema.version
            ))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.RETRIEVED_ACTIVE_SUCCESS.format(
                    name=schema.schema_name,
                    version=schema.version
                ),
                data=ClientSchemaResponse(
                    _id=str(schema.id),
                    client_id=schema.client_id,
                    schema_name=schema.schema_name,
                    version=schema.version,
                    is_active=schema.is_active,
                    description=schema.description,
                    fields=schema.fields,
                    created_at=schema.created_at,
                    updated_at=schema.updated_at
                ).model_dump(by_alias=True)
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.RETRIEVE_ERROR.format(error=str(e))
            )
    
    @staticmethod
    async def update(schema_id: str, schema_data: ClientSchemaUpdate):
        """
        Update a client schema
        Updates the existing document in place
        """
        try:
            schema = await ClientSchema.get(PydanticObjectId(schema_id))
            
            if not schema:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientSchemaMessages.NOT_FOUND.format(id=schema_id)
                )
            
            # Update fields if provided
            if schema_data.description is not None:
                schema.description = schema_data.description
            
            if schema_data.fields is not None:
                schema.fields = [field.model_dump() for field in schema_data.fields]
            
            # Handle is_active flag
            if schema_data.is_active is not None and schema_data.is_active != schema.is_active:
                if schema_data.is_active:
                    # Deactivate all other versions
                    other_schemas = await ClientSchema.find(
                        ClientSchema.client_id == schema.client_id,
                        ClientSchema.schema_name == schema.schema_name,
                        ClientSchema.id != schema.id
                    ).to_list()
                    
                    for other in other_schemas:
                        if other.is_active:
                            other.is_active = False
                            other.updated_at = datetime.now(timezone.utc)
                            await other.save()
                
                schema.is_active = schema_data.is_active
            
            schema.updated_at = datetime.now(timezone.utc)
            await schema.save()
            
            logger.info(ClientSchemaMessages.UPDATED_SUCCESS.format(
                name=schema.schema_name,
                version=schema.version
            ))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.UPDATED_SUCCESS.format(
                    name=schema.schema_name,
                    version=schema.version
                ),
                data=ClientSchemaResponse(
                    _id=str(schema.id),
                    client_id=schema.client_id,
                    schema_name=schema.schema_name,
                    version=schema.version,
                    is_active=schema.is_active,
                    description=schema.description,
                    fields=schema.fields,
                    created_at=schema.created_at,
                    updated_at=schema.updated_at
                ).model_dump(by_alias=True)
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(ClientSchemaMessages.UPDATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.UPDATE_ERROR.format(error=str(e))
            )
    
    @staticmethod
    async def activate_version(schema_id: str):
        """
        Activate a specific version of a schema
        Deactivates all other versions of the same schema
        """
        try:
            schema = await ClientSchema.get(PydanticObjectId(schema_id))
            
            if not schema:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientSchemaMessages.NOT_FOUND.format(id=schema_id)
                )
            
            # Deactivate all other versions
            other_schemas = await ClientSchema.find(
                ClientSchema.client_id == schema.client_id,
                ClientSchema.schema_name == schema.schema_name,
                ClientSchema.id != schema.id
            ).to_list()
            
            for other in other_schemas:
                if other.is_active:
                    other.is_active = False
                    other.updated_at = datetime.now(timezone.utc)
                    await other.save()
            
            # Activate this version
            schema.is_active = True
            schema.updated_at = datetime.now(timezone.utc)
            await schema.save()
            
            logger.info(ClientSchemaMessages.ACTIVATED_SUCCESS.format(
                name=schema.schema_name,
                version=schema.version
            ))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.ACTIVATED_SUCCESS.format(
                    name=schema.schema_name,
                    version=schema.version
                ),
                data=ClientSchemaResponse(
                    _id=str(schema.id),
                    client_id=schema.client_id,
                    schema_name=schema.schema_name,
                    version=schema.version,
                    is_active=schema.is_active,
                    description=schema.description,
                    fields=schema.fields,
                    created_at=schema.created_at,
                    updated_at=schema.updated_at
                ).model_dump(by_alias=True)
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(ClientSchemaMessages.ACTIVATE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.ACTIVATE_ERROR.format(error=str(e))
            )
    
    @staticmethod
    async def delete(schema_id: str):
        """Delete a client schema"""
        try:
            schema = await ClientSchema.get(PydanticObjectId(schema_id))
            
            if not schema:
                raise HTTPException(
                    status_code=StatusCode.NOT_FOUND,
                    detail=ClientSchemaMessages.NOT_FOUND.format(id=schema_id)
                )
            
            await schema.delete()
            
            logger.info(ClientSchemaMessages.DELETED_SUCCESS.format(id=schema_id))
            
            return APIResponse(
                success=True,
                message=ClientSchemaMessages.DELETED_SUCCESS.format(id=schema_id),
                data=None
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(ClientSchemaMessages.DELETE_ERROR.format(error=str(e)))
            raise HTTPException(
                status_code=StatusCode.BAD_REQUEST,
                detail=ClientSchemaMessages.DELETE_ERROR.format(error=str(e))
            )