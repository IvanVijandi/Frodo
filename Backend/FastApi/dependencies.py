from fastapi import Request, Depends
from typing import Optional

try:
    from Langchain.embbedings import EmbeddingGenerator
    from Langchain.Reranker import Reranker
    from Milvus.main import Async_Milvus_Client
    from Postgres import get_db
except ModuleNotFoundError:
    from Backend.Langchain.embbedings import EmbeddingGenerator
    from Backend.Langchain.Reranker import Reranker
    from Backend.Milvus.main import Async_Milvus_Client
    from Backend.Postgres import get_db

from .use_cases.buckets import (
    CreateBucketUseCase,
    ListBucketsUseCase,
    GetBucketUseCase,
    DeleteBucketUseCase,
)
from .use_cases.ingestion import IngestPdfUseCase
from .use_cases.rag import (
    SearchDocumentsUseCase,
    GenerateResponseUseCase,
)

# ------------------------------------------------------------------------------
# Servicios compartidos (del app.state configurados en lifespan)
# ------------------------------------------------------------------------------

def get_milvus_client(request: Request) -> Async_Milvus_Client:
    return request.app.state.milvus_client

def get_embedding_generator(request: Request) -> EmbeddingGenerator:
    return request.app.state.embedding_generator

def get_reranker(request: Request) -> Optional[Reranker]:
    return getattr(request.app.state, "reranker", None)

# ------------------------------------------------------------------------------
# Inyección de Casos de Uso
# ------------------------------------------------------------------------------

def get_create_bucket_use_case(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    db = Depends(get_db),
) -> CreateBucketUseCase:
    return CreateBucketUseCase(milvus_client, db)

def get_list_buckets_use_case(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
) -> ListBucketsUseCase:
    return ListBucketsUseCase(milvus_client)

def get_get_bucket_use_case(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
) -> GetBucketUseCase:
    return GetBucketUseCase(milvus_client)

def get_delete_bucket_use_case(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    db = Depends(get_db),
) -> DeleteBucketUseCase:
    return DeleteBucketUseCase(milvus_client, db)

def get_ingest_pdf_use_case(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator)
) -> IngestPdfUseCase:
    return IngestPdfUseCase(milvus_client, embedding_generator)

def get_search_documents_use_case(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator),
    reranker: Optional[Reranker] = Depends(get_reranker)
) -> SearchDocumentsUseCase:
    return SearchDocumentsUseCase(milvus_client, embedding_generator, reranker)

def get_generate_response_use_case(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator),
    reranker: Optional[Reranker] = Depends(get_reranker)
) -> GenerateResponseUseCase:
    return GenerateResponseUseCase(milvus_client, embedding_generator, reranker)

