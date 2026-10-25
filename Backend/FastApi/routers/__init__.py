from .system import router as system_router
from .buckets import router as buckets_router
from .ingestion import router as ingestion_router
from .rag import router as rag_router
from .conversaciones import router as conversaciones_router

__all__ = [
    "system_router",
    "buckets_router",
    "ingestion_router",
    "rag_router",
    "conversaciones_router",
]

