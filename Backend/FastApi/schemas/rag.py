from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="Pregunta o consulta del usuario", example="¿Cuáles son las cláusulas de rescisión del contrato?")
    bucket_name: Optional[str] = Field("general", description="Nombre del bucket sobre el que realizar la búsqueda", example="general")
    conversacion_id: Optional[str] = Field(None, description="UUID de la conversación donde se persistirán la pregunta y la respuesta en PostgreSQL")
    stream: Optional[bool] = Field(True, description="Si es True, transmite la respuesta en tiempo real vía SSE (Server-Sent Events)")

