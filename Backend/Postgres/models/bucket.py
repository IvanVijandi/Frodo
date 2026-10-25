import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Dict, Any, List
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..connection import Base

if TYPE_CHECKING:
    from .conversacion import Conversacion

class Bucket(Base):
    __tablename__ = "buckets"

    # Clave primaria UUID generada en el backend
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Nombre identificador único del bucket (se corresponde con la colección vectorial de Milvus)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    # Categoría temática (ej: legal, finanzas, general)
    content_type: Mapped[str] = mapped_column(
        String(100),
        default="general",
        nullable=False,
    )
    # Descripción del propósito del bucket
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    # Metadatos flexibles en formato JSON
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

    # Relación 1:N con conversaciones pertenecientes a este bucket
    conversaciones: Mapped[List["Conversacion"]] = relationship(
        "Conversacion",
        back_populates="bucket",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Bucket(id={self.id}, name='{self.name}', content_type='{self.content_type}')>"

