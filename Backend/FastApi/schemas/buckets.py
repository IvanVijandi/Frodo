from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class BucketCreateRequest(BaseModel):
    name: str = Field(..., description="Nombre del bucket (ej: 'legal_docs', 'finanzas_2026')", example="legal_docs")
    content_type: str = Field("general", description="Categoría temática del contenido", example="legal")
    description: Optional[str] = Field("", description="Descripción del propósito del bucket", example="Contratos y normativas legales")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Metadatos adicionales en formato clave-valor", example={"tags": ["contratos", "2026"]})

