from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional
from ..dependencies import get_ingest_pdf_use_case
from ..use_cases.ingestion import IngestPdfUseCase

router = APIRouter(tags=["Ingesta"])

@router.post(
    "/upload-file",
    summary="Subir e indexar un documento PDF en un bucket",
    description="Recibe un archivo PDF, divide su contenido en fragmentos textuales, genera sus embeddings vectoriales y los almacena en el bucket seleccionado."
)
async def upload_file(
    file: UploadFile = File(..., description="Archivo PDF para procesar e indexar"),
    bucket_name: str = Form("general", description="Bucket de destino para almacenar el documento"),
    content_type: Optional[str] = Form(None, description="Tipo de contenido opcional (si se omite, hereda el del bucket)"),
    use_case: IngestPdfUseCase = Depends(get_ingest_pdf_use_case)
):
    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se admiten archivos PDF."
        )

    try:
        content = await file.read()
        return await use_case.execute(
            file_bytes=content,
            filename=file.filename,
            bucket_name=bucket_name,
            content_type=content_type
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {e}"
        )

