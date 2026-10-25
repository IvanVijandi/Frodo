import logging
from .connection import engine, Base
# Importar modelos para que queden registrados en el catálogo de Base.metadata
from .models import Bucket, Conversacion, Mensaje  # noqa: F401

logger = logging.getLogger("maria.postgres")

async def init_postgres_db():
    """
    Inicializa de forma asíncrona las tablas en PostgreSQL si aún no existen.
    Crea: 'buckets', 'conversaciones' y 'mensajes'.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tablas de PostgreSQL ('buckets', 'conversaciones', 'mensajes') listas y verificadas.")
    except Exception as e:
        print(f"⚠ Advertencia durante init_postgres_db: {e}")
        # No bloqueamos el arranque en caso de que Postgres tarde unos segundos en responder
        raise e

