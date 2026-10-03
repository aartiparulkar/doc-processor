import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from doc_processor.api.dependencies import CurrentUserDep, DocumentServiceDep
from doc_processor.schemas.documents import DocumentResponse, ProcessingStatusResponse

router = APIRouter(prefix="/documents")


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MiB


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    current_user: CurrentUserDep,
    document_service: DocumentServiceDep,
    file: UploadFile = File(...),
) -> DocumentResponse:
    try:
        # Validate the declared MIME type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are allowed.",
            )

        # Read one byte beyond the allowed limit
        content = await file.read(MAX_FILE_SIZE + 1)

        # Reject empty files
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The upload file cannot be empty."
            )
        
        # Reject files larger than 10MiB
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="PDF file exceeds the 10 MB limit.",
            )

        # Check the PDF signature
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Invalid PDF file content."
            )
            
        if not file.filename or not file.filename.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A filename is required"
            )
            
        if len(file.filename) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename must not exceed 255 characters."
            )
            
        # Delegate storage and db operations.
        document = await document_service.upload_document(
            user_id=current_user.id,
            filename=file.filename,
            content=content,
        )
        
        # Convert the SQLAlchemy model into the API response
        return DocumentResponse.model_validate(document)

    finally:
        await file.close()

        
@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    document_id: uuid.UUID,
    current_user: CurrentUserDep,
    document_service: DocumentServiceDep,
) -> DocumentResponse:
    
    document = await document_service.get_owned_document(
        document_id=document_id,
        user_id=current_user.id,
    )
    
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document Not Found",
        )
    
    return DocumentResponse.model_validate(document)


@router.get(
    "",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
) 
async def list_documents(
    current_user: CurrentUserDep,
    document_service: DocumentServiceDep,    
)-> list[DocumentResponse]:
    documents = await document_service.list_owned_document(user_id=current_user.id)
    
    return [
        DocumentResponse.model_validate(document)
        for document in documents
    ]


@router.delete(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_document(
    document_id: uuid.UUID,
    current_user: CurrentUserDep,
    document_service: DocumentServiceDep,
) -> DocumentResponse:

    document = await document_service.delete_owned_document(
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document Not Found",
        )

    return DocumentResponse.model_validate(document)


@router.get(
    "/{document_id}/status",
    response_model=ProcessingStatusResponse,
)
async def get_document_processing_status(
    document_id: uuid.UUID,
    current_user: CurrentUserDep,
    document_service: DocumentServiceDep,
) -> ProcessingStatusResponse:
    job = await document_service.get_owned_processing_job(
        document_id=document_id,
        user_id=current_user.id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or processing job not found.",
        )

    return ProcessingStatusResponse(
        document_id=job.document_id,
        status=job.status,
    )