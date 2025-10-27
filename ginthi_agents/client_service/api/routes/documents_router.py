from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from client_service.api.dependencies import get_database_session
from client_service.services.document_service import DocumentService
from client_service.schemas.base_response import APIResponse
from client_service.schemas.pydantic_schemas import DocumentCreate, DocumentUpdate

router = APIRouter()


@router.post(
    "/documents/create",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a document in dynamic collection",
    description="Creates a new document in a collection based on schema definition. "
                "Use when: 'create purchase order', 'add invoice', 'new GRN document'. "
                "The collection must have an active schema defined first."
)
async def create_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Create a new document in a dynamic collection.
    
    Steps:
    1. Validates client exists in PostgreSQL
    2. Fetches active schema for the collection
    3. Validates document data against schema rules
    4. Creates document in MongoDB collection
    
    Returns:
        APIResponse with created document details
    """
    return await DocumentService.create(
        client_id=document_data.client_id,
        collection_name=document_data.collection_name,
        data=document_data.data,
        db=db,
        created_by=document_data.created_by
    )

@router.get(
    "/documents/{client_id}/{collection_name}/{document_id}",
    response_model=APIResponse,
    summary="Get document by ID",
    description="Retrieves a specific document from a dynamic collection. "
                "Use when: 'get purchase order', 'show invoice details', 'find document by id'."
)
async def get_document(
    client_id: str,
    collection_name: str,
    document_id: str,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get a document by its MongoDB ObjectId.
    
    Args:
        client_id: UUID of the client
        collection_name: Name of the collection (schema_name)
        document_id: MongoDB ObjectId as string
    
    Returns:
        APIResponse with document data
    """
    return await DocumentService.get_by_id(
        client_id=client_id,
        collection_name=collection_name,
        document_id=document_id,
        db=db
    )


@router.get(
    "/documents/{client_id}/{collection_name}",
    response_model=APIResponse,
    summary="List all documents in collection",
    description="Retrieves all documents for a client in a specific collection. "
                "Use when: 'list all purchase orders', 'show all invoices', 'get all GRNs'. "
                "Supports pagination with skip and limit parameters."
)
async def get_all_documents(
    client_id: str,
    collection_name: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get all documents in a collection for a specific client.
    
    Args:
        client_id: UUID of the client
        collection_name: Name of the collection (schema_name)
        skip: Number of documents to skip (for pagination)
        limit: Maximum number of documents to return (max 100)
    
    Returns:
        APIResponse with list of documents
    """
    return await DocumentService.get_all(
        client_id=client_id,
        collection_name=collection_name,
        db=db,
        skip=skip,
        limit=limit
    )


@router.put(
    "/documents/{client_id}/{collection_name}/{document_id}",
    response_model=APIResponse,
    summary="Update document",
    description="Updates an existing document in a dynamic collection. "
                "Use when: 'update purchase order', 'modify invoice', 'change document status'. "
                "Only provided fields will be updated."
)
async def update_document(
    client_id: str,
    collection_name: str,
    document_id: str,
    update_data: DocumentUpdate,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Update a document in a dynamic collection.
    
    Steps:
    1. Validates client and document exist
    2. Validates update data against schema
    3. Updates only the provided fields
    4. Updates updated_at timestamp
    
    Args:
        client_id: UUID of the client
        collection_name: Name of the collection
        document_id: MongoDB ObjectId
        update_data: Updated field values
    
    Returns:
        APIResponse with updated document
    """
    return await DocumentService.update(
        client_id=client_id,
        collection_name=collection_name,
        document_id=document_id,
        data=update_data.data,
        db=db,
        updated_by=update_data.updated_by
    )


@router.delete(
    "/documents/{client_id}/{collection_name}/{document_id}",
    response_model=APIResponse,
    summary="Delete document",
    description="Permanently deletes a document from a dynamic collection. "
                "Use when: 'delete purchase order', 'remove invoice', 'delete document'."
)
async def delete_document(
    client_id: str,
    collection_name: str,
    document_id: str,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Delete a document from a dynamic collection.
    
    Args:
        client_id: UUID of the client
        collection_name: Name of the collection
        document_id: MongoDB ObjectId
    
    Returns:
        APIResponse confirming deletion
    """
    return await DocumentService.delete(
        client_id=client_id,
        collection_name=collection_name,
        document_id=document_id,
        db=db

    )
