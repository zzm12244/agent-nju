from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class KnowledgeDocument(BaseModel):
    id: str
    file_name: str
    stored_name: str
    chunks_indexed: int
    uploaded_at: str


class KnowledgeDocumentList(BaseModel):
    items: list[KnowledgeDocument]


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=10, description='The writing goal or draft request.')
    tone: str = Field(default='professional')
    audience: str = Field(default='general')
    source_url: HttpUrl | None = None
    use_knowledge_base: bool = True
    use_web_search: bool = True
    top_k: int = Field(default=4, ge=1, le=10)


class SourceSnippet(BaseModel):
    source_type: Literal['knowledge_base', 'web']
    title: str
    excerpt: str


class GenerateResponse(BaseModel):
    content: str
    sources: list[SourceSnippet]


class HealthResponse(BaseModel):
    status: str = 'ok'


class ActionResponse(BaseModel):
    message: str
