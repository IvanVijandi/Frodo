import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Bucket, Conversacion, Mensaje

# ============================================================================
# Operaciones para Buckets
# ============================================================================

async def get_bucket_by_id(db: AsyncSession, bucket_id: uuid.UUID) -> Optional[Bucket]:
    """Obtiene un bucket por su UUID."""
    result = await db.execute(select(Bucket).where(Bucket.id == bucket_id))
    return result.scalar_one_or_none()

async def get_bucket_by_name(db: AsyncSession, name: str) -> Optional[Bucket]:
    """Obtiene un bucket por su nombre único."""
    result = await db.execute(select(Bucket).where(Bucket.name == name))
    return result.scalar_one_or_none()

async def list_all_buckets(db: AsyncSession) -> List[Bucket]:
    """Lista todos los buckets registrados ordenados por fecha de creación descendente."""
    result = await db.execute(select(Bucket).order_by(desc(Bucket.created_at)))
    return list(result.scalars().all())

async def create_bucket(
    db: AsyncSession,
    name: str,
    content_type: str = "general",
    description: Optional[str] = "",
    extra_metadata: Optional[Dict[str, Any]] = None,
    bucket_id: Optional[uuid.UUID] = None,
) -> Bucket:
    """Crea y persiste un nuevo bucket."""
    bucket = Bucket(
        id=bucket_id or uuid.uuid4(),
        name=name,
        content_type=content_type,
        description=description,
        extra_metadata=extra_metadata or {},
    )
    db.add(bucket)
    await db.flush()
    return bucket

async def get_or_create_bucket(
    db: AsyncSession,
    name: str,
    content_type: str = "general",
    description: Optional[str] = "",
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Bucket:
    """Obtiene un bucket existente o lo crea si aún no está registrado en PostgreSQL."""
    bucket = await get_bucket_by_name(db, name)
    if not bucket:
        bucket = await create_bucket(
            db=db,
            name=name,
            content_type=content_type or "general",
            description=description or "",
            extra_metadata=extra_metadata or {},
        )
    return bucket

async def delete_bucket_by_name(db: AsyncSession, name: str) -> bool:
    """Elimina un bucket por su nombre (borra en cascada sus conversaciones y mensajes)."""
    bucket = await get_bucket_by_name(db, name)
    if not bucket:
        return False
    await db.delete(bucket)
    await db.flush()
    return True


# ============================================================================
# Operaciones para Conversaciones
# ============================================================================

async def create_conversacion(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    title: str = "Nueva Conversación",
    extra_metadata: Optional[Dict[str, Any]] = None,
    conversacion_id: Optional[uuid.UUID] = None,
) -> Conversacion:
    """Crea una nueva conversación asociada a un bucket."""
    conversacion = Conversacion(
        id=conversacion_id or uuid.uuid4(),
        bucket_id=bucket_id,
        title=title,
        extra_metadata=extra_metadata or {},
    )
    db.add(conversacion)
    await db.flush()
    return conversacion

async def get_conversacion(
    db: AsyncSession,
    conversacion_id: uuid.UUID,
    include_mensajes: bool = True,
) -> Optional[Conversacion]:
    """Obtiene una conversación por su ID, opcionalmente cargando todos sus mensajes."""
    query = select(Conversacion).where(Conversacion.id == conversacion_id)
    if include_mensajes:
        query = query.options(selectinload(Conversacion.mensajes))
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def list_conversaciones_by_bucket(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    limit: int = 50,
) -> List[Conversacion]:
    """Lista las conversaciones más recientes de un bucket."""
    result = await db.execute(
        select(Conversacion)
        .where(Conversacion.bucket_id == bucket_id)
        .order_by(desc(Conversacion.updated_at))
        .limit(limit)
    )
    return list(result.scalars().all())

async def delete_conversacion(db: AsyncSession, conversacion_id: uuid.UUID) -> bool:
    """Elimina una conversación y todos sus mensajes en cascada."""
    conversacion = await get_conversacion(db, conversacion_id, include_mensajes=False)
    if not conversacion:
        return False
    await db.delete(conversacion)
    await db.flush()
    return True


# ============================================================================
# Operaciones para Mensajes
# ============================================================================

async def add_mensaje(
    db: AsyncSession,
    conversacion_id: uuid.UUID,
    role: str,
    content: str,
    sources: Optional[List[Any]] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
    mensaje_id: Optional[uuid.UUID] = None,
) -> Mensaje:
    """Añade un mensaje a una conversación."""
    mensaje = Mensaje(
        id=mensaje_id or uuid.uuid4(),
        conversacion_id=conversacion_id,
        role=role,
        content=content,
        sources=sources or [],
        extra_metadata=extra_metadata or {},
    )
    db.add(mensaje)
    await db.flush()
    return mensaje

async def get_mensajes_by_conversacion(
    db: AsyncSession,
    conversacion_id: uuid.UUID,
) -> List[Mensaje]:
    """Obtiene el historial completo de mensajes de una conversación ordenados por fecha."""
    result = await db.execute(
        select(Mensaje)
        .where(Mensaje.conversacion_id == conversacion_id)
        .order_by(Mensaje.created_at)
    )
    return list(result.scalars().all())

