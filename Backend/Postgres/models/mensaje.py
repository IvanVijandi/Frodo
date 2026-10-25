import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Any, List
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..connection import Base

if TYPE_CHECKING:
    from .conversacion import Conversacion

class Mensaje(Base):
    __tablename__ = "mensajes"

    # Clave primaria UUID generada en el backend
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Llave foránea hacia la conversación a la que pertenece el mensaje
    conversacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Rol del emisor: 'user', 'assistant', 'system'
    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    # Contenido textual del mensaje
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    # Citas y fragmentos RAG recuperados desde Milvus que fundamentan la respuesta
    sources: Mapped[List[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    # Metadatos del mensaje (tokens consumidos, latencia, modelo LLM utilizado, etc.)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    # Marca de tiempo UTC indexada para consultas cronológicas eficientes
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relación N:1 con la conversación
    conversacion: Mapped["Conversacion"] = relationship(
        "Conversacion",
        back_populates="mensajes",
    )

    def __repr__(self) -> str:
        return f"<Mensaje(id={self.id}, conversacion_id={self.conversacion_id}, role='{self.role}')>"

