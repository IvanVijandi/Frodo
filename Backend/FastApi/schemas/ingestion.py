from pydantic import BaseModel, Field

class IngestResponse(BaseModel):
    message: str = Field(..., description="Mensaje de confirmación del procesamiento")
    bucket: str = Field(..., description="Nombre del bucket donde se almacenó el documento")
    content_type: str = Field(..., description="Tipo de contenido asignado")
    chunks_procesados: int = Field(..., description="Cantidad de fragmentos procesados e insertados")

