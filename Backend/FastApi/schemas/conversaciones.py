from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ConversacionCreateRequest(BaseModel):
    bucket_name: str = Field(..., description="Nombre del bucket al que pertenece la conversación", example="general")
    title: Optional[str] = Field("Nueva conversación", description="Título descriptivo del hilo de chat", example="Consulta sobre normativas")
    extra_metadata: Optional[Dict[str, Any]] = Field({}, description="Metadatos adicionales de configuración o sesión")

class MensajeCreateRequest(BaseModel):
    role: str = Field(..., description="Rol del autor: 'user', 'assistant' o 'system'", example="user")
    content: str = Field(..., description="Contenido textual del mensaje", example="¿Cuál es el plazo de entrega?")
    sources: Optional[List[Any]] = Field([], description="Fuentes y fragmentos documentales recuperados")
    extra_metadata: Optional[Dict[str, Any]] = Field({}, description="Metadatos como tokens, modelo, latencia")

class MensajeResponse(BaseModel):
    id: str
    conversacion_id: str
    role: str
    content: str
    sources: List[Any] = []
    extra_metadata: Dict[str, Any] = {}
    created_at: str

class ConversacionResponse(BaseModel):
    id: str
    bucket_id: str
    bucket_name: Optional[str] = None
    title: str
    extra_metadata: Dict[str, Any] = {}
    created_at: str
    updated_at: str
    mensajes: Optional[List[MensajeResponse]] = None

