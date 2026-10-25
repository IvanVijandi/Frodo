import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Any, List
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..connection import Base

if TYPE_CHECKING:
    from .bucket import Bucket
    from .mensaje import Mensaje

class Conversacion(Base):
    __tablename__ = "conversaciones"

    # Clave primaria UUID generada en el backend
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Llave foránea hacia el bucket temático al que pertenece este thread
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buckets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Título descriptivo de la conversación
    title: Mapped[str] = mapped_column(
        String(255),
        default="Nueva Conversación",
        nullable=False,
    )
    # Metadatos de la conversación (parámetros de generación, tags, etc.)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    # Marcas de tiempo UTC
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relación N:1 con el bucket
    bucket: Mapped["Bucket"] = relationship(
        "Bucket",
        back_populates="conversaciones",
    )
    # Relación 1:N con los mensajes del hilo (ordenados cronológicamente)
    mensajes: Mapped[List["Mensaje"]] = relationship(
        "Mensaje",
        back_populates="conversacion",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Mensaje.created_at",
    )

    def __repr__(self) -> str:
        return f"<Conversacion(id={self.id}, title='{self.title}', bucket_id={self.bucket_id})>"

