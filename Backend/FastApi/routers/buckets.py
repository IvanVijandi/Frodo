from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.buckets import BucketCreateRequest
from ..dependencies import (
    get_create_bucket_use_case,
    get_list_buckets_use_case,
    get_get_bucket_use_case,
    get_delete_bucket_use_case,
    get_milvus_client,
)
from ..use_cases.buckets import (
    CreateBucketUseCase,
    ListBucketsUseCase,
    GetBucketUseCase,
    DeleteBucketUseCase,
)

router = APIRouter(tags=["Buckets"])

@router.get(
    "/buckets",
    summary="Listar todos los buckets registrados",
    description="Devuelve la lista de todos los buckets con su tipo de contenido, descripción, fecha de creación y conteo de fragmentos indexados."
)
async def list_buckets(
    use_case: ListBucketsUseCase = Depends(get_list_buckets_use_case)
):
    try:
        return await use_case.execute()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar buckets: {e}"
        )

@router.post(
    "/buckets",
    summary="Crear un nuevo bucket",
    description="Crea una nueva colección vectorial en Milvus con índice optimizado y registra sus metadatos de tipo de contenido."
)
async def create_bucket(
    request: BucketCreateRequest,
    use_case: CreateBucketUseCase = Depends(get_create_bucket_use_case)
):
    try:
        return await use_case.execute(
            name=request.name,
            content_type=request.content_type,
            description=request.description,
            metadata=request.metadata
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el bucket: {e}"
        )

@router.get(
    "/buckets/{bucket_name}",
    summary="Obtener detalles de un bucket",
    description="Consulta la información detallada, metadatos y cantidad de chunks de un bucket por su nombre."
)
async def get_bucket(
    bucket_name: str,
    use_case: GetBucketUseCase = Depends(get_get_bucket_use_case)
):
    bucket_info = await use_case.execute(bucket_name)
    if not bucket_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El bucket '{bucket_name}' no existe."
        )
    return {"bucket": bucket_info}

@router.delete(
    "/buckets/{bucket_name}",
    summary="Eliminar un bucket",
    description="Elimina la colección física en Milvus y su registro de metadatos. El bucket por defecto 'general' está protegido."
)
async def delete_bucket(
    bucket_name: str,
    use_case: DeleteBucketUseCase = Depends(get_delete_bucket_use_case)
):
    try:
        return await use_case.execute(bucket_name)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el bucket: {e}"
        )

@router.get(
    "/buckets/{bucket_name}/documents",
    summary="Listar documentos indexados en un bucket",
    description="Devuelve todos los archivos PDF indexados en la colección vectorial del bucket con su conteo de fragmentos."
)
async def list_bucket_documents(
    bucket_name: str,
    milvus_client = Depends(get_milvus_client),
):
    try:
        documents = await milvus_client.list_documents(bucket_name)
        return {"bucket": bucket_name, "documents": documents}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar documentos del bucket: {e}"
        )

@router.delete(
    "/buckets/{bucket_name}/documents/{filename}",
    summary="Eliminar un documento del bucket",
    description="Elimina todos los fragmentos vectoriales asociados a un archivo dentro del bucket especificado."
)
async def delete_bucket_document(
    bucket_name: str,
    filename: str,
    milvus_client = Depends(get_milvus_client),
):
    try:
        success = await milvus_client.delete_document(bucket_name, filename)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el documento '{filename}' en el bucket '{bucket_name}'."
            )
        return {"message": f"Documento '{filename}' eliminado exitosamente del bucket '{bucket_name}'."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar documento del bucket: {e}"
        )

