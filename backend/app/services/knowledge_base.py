from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from langchain_community.document_loaders import TextLoader, UnstructuredFileLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.models import KnowledgeDocument, SourceSnippet

SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf', '.doc', '.docx'}


class KnowledgeBaseService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.embedding_model,
            api_key=self.settings.embedding_api_key,
            base_url=self.settings.embedding_base_url,
            timeout=self.settings.embedding_timeout_seconds,
            max_retries=1,
            check_embedding_ctx_length=False,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
        )

    async def save_upload(self, file: UploadFile) -> Path:
        suffix = Path(file.filename or 'upload.txt').suffix.lower() or '.txt'
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f'Unsupported file type: {suffix}. Supported types: {", ".join(sorted(SUPPORTED_EXTENSIONS))}')

        output_path = self.settings.uploads_dir / f'{uuid4().hex}{suffix}'
        content = await file.read()
        output_path.write_bytes(content)
        return output_path

    def ingest_file(self, file_path: Path, original_name: str) -> KnowledgeDocument:
        document_id = uuid4().hex
        chunks = self._build_chunks(file_path, document_id)
        if not chunks:
            raise ValueError('The uploaded document did not produce any indexable content.')

        vector_store = self._load_or_create_store()
        vector_store.add_documents(chunks)
        vector_store.save_local(str(self.settings.vector_store_dir))

        record = KnowledgeDocument(
            id=document_id,
            file_name=original_name,
            stored_name=file_path.name,
            chunks_indexed=len(chunks),
            uploaded_at=datetime.now(timezone.utc).isoformat(),
        )
        records = self._read_registry()
        records.append(record)
        self._write_registry(records)
        return record

    def list_documents(self) -> list[KnowledgeDocument]:
        return self._read_registry()

    def delete_document(self, document_id: str) -> bool:
        records = self._read_registry()
        remaining = [item for item in records if item.id != document_id]
        if len(remaining) == len(records):
            return False

        target = next(item for item in records if item.id == document_id)
        file_path = self.settings.uploads_dir / target.stored_name
        if file_path.exists():
            file_path.unlink()

        self._write_registry(remaining)
        self.rebuild_index(remaining)
        return True

    def rebuild_index(self, records: list[KnowledgeDocument] | None = None) -> None:
        records = records if records is not None else self._read_registry()
        documents: list[Document] = []
        for record in records:
            file_path = self.settings.uploads_dir / record.stored_name
            if not file_path.exists():
                continue
            documents.extend(self._build_chunks(file_path, record.id))

        self._clear_vector_store()
        vector_store = FAISS.from_documents(
            [Document(page_content='Knowledge base bootstrap', metadata={'source': 'system'})],
            self.embeddings,
        )
        if documents:
            vector_store.add_documents(documents)
        vector_store.save_local(str(self.settings.vector_store_dir))

        refreshed_records: list[KnowledgeDocument] = []
        for record in records:
            file_path = self.settings.uploads_dir / record.stored_name
            if not file_path.exists():
                continue
            chunk_count = len(self._build_chunks(file_path, record.id))
            refreshed_records.append(record.model_copy(update={'chunks_indexed': chunk_count}))
        self._write_registry(refreshed_records)

    def search(self, query: str, top_k: int = 4) -> list[SourceSnippet]:
        if not (self.settings.vector_store_dir / 'index.faiss').exists():
            return []

        file_lookup = {item.id: item.file_name for item in self._read_registry()}
        vector_store = FAISS.load_local(
            str(self.settings.vector_store_dir),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        results = vector_store.similarity_search(query, k=top_k + 2)
        snippets: list[SourceSnippet] = []
        for doc in results:
            if doc.metadata.get('source') == 'system':
                continue
            doc_id = doc.metadata.get('document_id')
            title = file_lookup.get(doc_id) or Path(doc.metadata.get('source', 'knowledge-base')).name
            snippets.append(
                SourceSnippet(
                    source_type='knowledge_base',
                    title=title,
                    excerpt=doc.page_content[:400],
                )
            )
            if len(snippets) >= top_k:
                break
        return snippets

    def _build_chunks(self, file_path: Path, document_id: str) -> list[Document]:
        documents = self._load_documents(file_path)
        chunks = self.splitter.split_documents(documents)
        for chunk in chunks:
            chunk.metadata['document_id'] = document_id
        return chunks

    def _load_documents(self, file_path: Path) -> list[Document]:
        suffix = file_path.suffix.lower()
        try:
            if suffix in {'.txt', '.md'}:
                loader = TextLoader(str(file_path), encoding='utf-8')
            else:
                loader = UnstructuredFileLoader(str(file_path))
            documents = loader.load()
        except Exception as exc:
            raise ValueError(f'Failed to parse {suffix} file: {exc}') from exc

        for doc in documents:
            doc.metadata['source'] = str(file_path)
        return documents

    def _load_or_create_store(self) -> FAISS:
        index_file = self.settings.vector_store_dir / 'index.faiss'
        if index_file.exists():
            return FAISS.load_local(
                str(self.settings.vector_store_dir),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        return FAISS.from_documents(
            [Document(page_content='Knowledge base bootstrap', metadata={'source': 'system'})],
            self.embeddings,
        )

    def _clear_vector_store(self) -> None:
        for file_name in ('index.faiss', 'index.pkl'):
            file_path = self.settings.vector_store_dir / file_name
            if file_path.exists():
                file_path.unlink()

    def _read_registry(self) -> list[KnowledgeDocument]:
        raw = json.loads(self.settings.knowledge_registry_path.read_text(encoding='utf-8'))
        return [KnowledgeDocument.model_validate(item) for item in raw]

    def _write_registry(self, records: list[KnowledgeDocument]) -> None:
        payload = [item.model_dump() for item in records]
        self.settings.knowledge_registry_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
