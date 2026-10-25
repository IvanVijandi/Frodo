import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_db
from ..schemas.conversaciones import (
    ConversacionCreateRequest,
    MensajeCreateRequest,
    ConversacionResponse,
    MensajeResponse,
)

try:
    from Postgres import repository
except ModuleNotFoundError:
    from Backend.Postgres import repository

router = APIRouter(tags=["Conversaciones & Mensajes"])

def _format_conversacion(conv, bucket_name: str = None) -> ConversacionResponse:
    mensajes_resp = None
    if getattr(conv, "mensajes", None) is not None:
        mensajes_resp = [
            MensajeResponse(
                id=str(m.id),
                conversacion_id=str(m.conversacion_id),
                role=m.role,
                content=m.content,
                sources=m.sources or [],
                extra_metadata=m.extra_metadata or {},
                created_at=m.created_at.isoformat() if hasattr(m.created_at, "isoformat") else str(m.created_at),
            )
            for m in conv.mensajes
        ]

    b_name = bucket_name
    if not b_name and getattr(conv, "bucket", None) is not None:
        b_name = conv.bucket.name

    return ConversacionResponse(
        id=str(conv.id),
        bucket_id=str(conv.bucket_id),
        bucket_name=b_name,
        title=conv.title,
        extra_metadata=conv.extra_metadata or {},
        created_at=conv.created_at.isoformat() if hasattr(conv.created_at, "isoformat") else str(conv.created_at),
        updated_at=conv.updated_at.isoformat() if hasattr(conv.updated_at, "isoformat") else str(conv.updated_at),
        mensajes=mensajes_resp,
    )

@router.post(
    "/conversaciones",
    response_model=ConversacionResponse,
    summary="Crear una nueva conversación",
    description="Crea un nuevo hilo de conversación vinculado a un bucket temático en PostgreSQL."
)
async def create_conversacion(
    request: ConversacionCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        bucket = await repository.get_or_create_bucket(db, name=request.bucket_name.strip())
        conv = await repository.create_conversacion(
            db=db,
            bucket_id=bucket.id,
            title=request.title or "Nueva conversación",
            extra_metadata=request.extra_metadata or {},
        )
        return _format_conversacion(conv, bucket_name=bucket.name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear conversación: {e}"
        )

@router.get(
    "/buckets/{bucket_name}/conversaciones",
    response_model=List[ConversacionResponse],
    summary="Listar conversaciones de un bucket",
    description="Obtiene todas las conversaciones asociadas al bucket ordenadas de la más reciente a la más antigua."
)
async def list_conversaciones_by_bucket(
    bucket_name: str,
    db: AsyncSession = Depends(get_db),
):
    bucket = await repository.get_bucket_by_name(db, bucket_name.strip())
    if not bucket:
        return []

    convs = await repository.list_conversaciones_by_bucket(db, bucket_id=bucket.id)
    return [_format_conversacion(c, bucket_name=bucket.name) for c in convs]

@router.get(
    "/conversaciones/{conversacion_id}",
    response_model=ConversacionResponse,
    summary="Obtener detalle de una conversación con su historial de mensajes",
    description="Recupera la conversación y todos sus mensajes en orden cronológico."
)
async def get_conversacion(
    conversacion_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        c_uuid = uuid.UUID(conversacion_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de conversación no es un UUID válido.")

    conv = await repository.get_conversacion(db, conversacion_id=c_uuid, include_mensajes=True)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada.")

    return _format_conversacion(conv)

@router.delete(
    "/conversaciones/{conversacion_id}",
    summary="Eliminar una conversación",
    description="Elimina la conversación y todos sus mensajes asociados en cascada."
)
async def delete_conversacion(
    conversacion_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        c_uuid = uuid.UUID(conversacion_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de conversación no es un UUID válido.")

    success = await repository.delete_conversacion(db, conversacion_id=c_uuid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada.")

    return {"message": "Conversación eliminada exitosamente."}

@router.post(
    "/conversaciones/{conversacion_id}/mensajes",
    response_model=MensajeResponse,
    summary="Agregar mensaje a una conversación",
    description="Inserta un mensaje (usuario, asistente o sistema) en el historial de la conversación."
)
async def add_mensaje_endpoint(
    conversacion_id: str,
    request: MensajeCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        c_uuid = uuid.UUID(conversacion_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de conversación no es un UUID válido.")

    conv = await repository.get_conversacion(db, conversacion_id=c_uuid, include_mensajes=False)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada.")

    msg = await repository.add_mensaje(
        db=db,
        conversacion_id=c_uuid,
        role=request.role,
        content=request.content,
        sources=request.sources or [],
        extra_metadata=request.extra_metadata or {},
    )

    return MensajeResponse(
        id=str(msg.id),
        conversacion_id=str(msg.conversacion_id),
        role=msg.role,
        content=msg.content,
        sources=msg.sources or [],
        extra_metadata=msg.extra_metadata or {},
        created_at=msg.created_at.isoformat() if hasattr(msg.created_at, "isoformat") else str(msg.created_at),
    )

