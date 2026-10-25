from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from ..schemas.rag import QueryRequest
from ..dependencies import (
    get_search_documents_use_case,
    get_generate_response_use_case,
)
from ..use_cases.rag import (
    SearchDocumentsUseCase,
    GenerateResponseUseCase,
)

router = APIRouter(tags=["RAG & Búsqueda"])

@router.post(
    "/get-document",
    summary="Búsqueda vectorial semántica en un bucket",
    description="Calcula el embedding de la consulta, recupera los fragmentos más cercanos en el bucket y aplica reranker si está disponible."
)
async def get_document_endpoint(
    request: QueryRequest,
    use_case: SearchDocumentsUseCase = Depends(get_search_documents_use_case)
):
    try:
        return await use_case.execute(
            query=request.query,
            bucket_name=request.bucket_name or "general"
        )
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke).strip("'"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la búsqueda: {e}"
        )

@router.post(
    "/generarRespuesta",
    summary="Generar respuesta RAG evaluada sobre un bucket",
    description="Recupera contexto del bucket seleccionado y genera la respuesta con streaming en vivo de Ollama o evaluada con LangGraph."
)
async def generar_respuesta_endpoint(
    request: QueryRequest,
    use_case: GenerateResponseUseCase = Depends(get_generate_response_use_case)
):
    target_bucket = request.bucket_name.strip() if request.bucket_name else "general"

    if request.stream:
        return StreamingResponse(
            use_case.execute_stream(query=request.query, bucket_name=target_bucket),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    try:
        return await use_case.execute_evaluated(query=request.query, bucket_name=target_bucket)
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke).strip("'"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la generación de respuesta: {e}"
        )

