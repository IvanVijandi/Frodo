import sys
import os

# Asegurar que el directorio de Backend (o /app en Docker) esté en sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from Langchain.embbedings import EmbeddingGenerator
    from Langchain.Reranker import Reranker
    from Milvus.main import Async_Milvus_Client
    from Milvus.setup_db import setup_database
    from Postgres import init_postgres_db
    from config import conf
except ModuleNotFoundError:
    from Backend.Langchain.embbedings import EmbeddingGenerator
    from Backend.Langchain.Reranker import Reranker
    from Backend.Milvus.main import Async_Milvus_Client
    from Backend.Milvus.setup_db import setup_database
    from Backend.Postgres import init_postgres_db
    from Backend.config import conf

from .routers import (
    system_router,
    buckets_router,
    ingestion_router,
    rag_router,
    conversaciones_router,
)

tags_metadata = [
    {
        "name": "Buckets",
        "description": "Operaciones para crear, listar, inspeccionar y eliminar colecciones vectoriales temáticas en Milvus.",
    },
    {
        "name": "Conversaciones & Mensajes",
        "description": "Persistencia de sesiones de chat, hilos temáticos e historial de mensajes en PostgreSQL.",
    },
    {
        "name": "Ingesta",
        "description": "Extracción de texto, fragmentación (chunking), generación de embeddings e indexación de PDFs.",
    },
    {
        "name": "RAG & Búsqueda",
        "description": "Búsqueda vectorial semántica con reranking y generación de respuestas fundamentadas evaluadas con LangGraph.",
    },
    {
        "name": "Sistema",
        "description": "Comprobación de estado y disponibilidad del servicio.",
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Asegurar base de datos, registro y bucket general en Milvus
    try:
        setup_database()
    except Exception as e:
        print(f"Advertencia durante setup_database en Milvus: {e}")

    # Inicializar tablas en PostgreSQL (buckets, conversaciones, mensajes)
    try:
        await init_postgres_db()
    except Exception as e:
        print(f"Advertencia durante init_postgres_db: {e}")

    app.state.reranker = Reranker() if conf.RERANKER_PROVIDER.lower() != "none" else None
    app.state.embedding_generator = EmbeddingGenerator()
    app.state.milvus_client = Async_Milvus_Client()
    yield

app = FastAPI(
    title="MARIA - RAG API & Knowledge Engine",
    description="""
# 🤖 MARIA - Asistente RAG Multi-Bucket (Arquitectura por Casos de Uso)

Bienvenido a la API modular de **MARIA**.
Esta plataforma organiza su lógica de negocio en casos de uso desacoplados:
* **Buckets**: Creación, listado, inspección y eliminación de colecciones temáticas.
* **Ingesta**: Extracción, fragmentación, generación de embeddings e indexación de PDFs.
* **RAG & Búsqueda**: Búsqueda semántica, reranking y generación con streaming en vivo (Ollama) o evaluada (LangGraph).
    """,
    version="2.1.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Montaje de routers organizados por casos de uso
app.include_router(system_router)
app.include_router(buckets_router)
app.include_router(ingestion_router)
app.include_router(rag_router)
app.include_router(conversaciones_router)
