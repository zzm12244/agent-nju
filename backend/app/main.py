from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import (
    ActionResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    KnowledgeDocument,
    KnowledgeDocumentList,
)
from app.services.knowledge_base import KnowledgeBaseService
from app.services.writer_agent import WriterAgentService

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

knowledge_base_service = KnowledgeBaseService()
writer_agent_service = WriterAgentService()


@app.get('/health', response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get('/api/knowledge/documents', response_model=KnowledgeDocumentList)
def list_knowledge_documents() -> KnowledgeDocumentList:
    return KnowledgeDocumentList(items=knowledge_base_service.list_documents())


@app.post('/api/knowledge/upload', response_model=KnowledgeDocument)
async def upload_knowledge(file: UploadFile = File(...)) -> KnowledgeDocument:
    try:
        saved_path = await knowledge_base_service.save_upload(file)
        return knowledge_base_service.ingest_file(saved_path, file.filename or saved_path.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Knowledge upload failed: {exc}') from exc


@app.delete('/api/knowledge/documents/{document_id}', response_model=ActionResponse)
def delete_knowledge_document(document_id: str) -> ActionResponse:
    deleted = knowledge_base_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Document not found')
    return ActionResponse(message='Document deleted and index rebuilt.')


@app.post('/api/knowledge/rebuild', response_model=ActionResponse)
def rebuild_knowledge_index() -> ActionResponse:
    knowledge_base_service.rebuild_index()
    return ActionResponse(message='Knowledge index rebuilt successfully.')


@app.post('/api/generate', response_model=GenerateResponse)
def generate_document(payload: GenerateRequest) -> GenerateResponse:
    return writer_agent_service.generate(payload)
