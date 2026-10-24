import sys
import os

# Asegurar que el directorio de Backend (o /app en Docker) esté en sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException, File, Form, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import tempfile
import time

try:
    from Langchain.embbedings import EmbeddingGenerator
    from Langchain.Splitter import Splitter
    from Langchain.Reranker import Reranker
    from Milvus.main import Async_Milvus_Client
    from Milvus.setup_db import setup_database
    from Langchain.graph import EvaluatorGraph
    from config import conf
except ModuleNotFoundError:
    from Backend.Langchain.embbedings import EmbeddingGenerator
    from Backend.Langchain.Splitter import Splitter
    from Backend.Langchain.Reranker import Reranker
    from Backend.Milvus.main import Async_Milvus_Client
    from Backend.Milvus.setup_db import setup_database
    from Backend.Langchain.graph import EvaluatorGraph
    from Backend.config import conf

## Lifespan: inicializa y cierra recursos al iniciar y detener el servidor.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Asegurar base de datos, registro y bucket general en Milvus
    setup_database()
    
    app.state.reranker = Reranker() if conf.RERANKER_PROVIDER.lower() != "none" else None
    app.state.embedding_generator = EmbeddingGenerator()
    app.state.milvus_client = Async_Milvus_Client()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Inyección de dependencias
def get_milvus_client(request: Request) -> Async_Milvus_Client:
    return request.app.state.milvus_client

def get_embedding_generator(request: Request) -> EmbeddingGenerator:
    return request.app.state.embedding_generator

def get_reranker(request: Request) -> Optional[Reranker]:
    return request.app.state.reranker

# Modelos Pydantic
class BucketCreateRequest(BaseModel):
    name: str
    content_type: str = "general"
    description: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = {}

class QueryRequest(BaseModel):
    query: str
    bucket_name: Optional[str] = "general"

## Health Check
@app.get("/")
async def ok():
    return {"message": "ok", "service": "MARIA Backend"}

# ==============================================================================
# Endpoints de Gestión de Buckets
# ==============================================================================

@app.get("/buckets")
async def list_buckets(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
    """Lista todos los buckets registrados en Milvus con sus metadatos y estadísticas."""
    try:
        buckets = await milvus_client.list_buckets()
        return {"buckets": buckets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar buckets: {e}")

@app.post("/buckets")
async def create_bucket(
    request: BucketCreateRequest,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
    """Crea un nuevo bucket con un tipo de contenido, descripción y metadatos específicos."""
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="El nombre del bucket no puede estar vacío.")

    try:
        bucket_info = await milvus_client.create_bucket(
            name=request.name,
            content_type=request.content_type,
            description=request.description,
            metadata=request.metadata
        )
        return {
            "message": f"Bucket '{bucket_info['name']}' creado exitosamente.",
            "bucket": bucket_info
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el bucket: {e}")

@app.get("/buckets/{bucket_name}")
async def get_bucket(
    bucket_name: str,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
    """Obtiene los detalles y metadatos de un bucket específico."""
    bucket_info = await milvus_client.get_bucket(bucket_name)
    if not bucket_info:
        raise HTTPException(status_code=404, detail=f"El bucket '{bucket_name}' no existe.")
    return {"bucket": bucket_info}

@app.delete("/buckets/{bucket_name}")
async def delete_bucket(
    bucket_name: str,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
    """Elimina un bucket y toda la información almacenada en su colección vectorial."""
    try:
        await milvus_client.delete_bucket(bucket_name)
        return {"message": f"Bucket '{bucket_name}' eliminado exitosamente."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el bucket: {e}")

# ==============================================================================
# Endpoints de Ingesta y Consulta
# ==============================================================================

@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    bucket_name: str = Form("general"),
    content_type: Optional[str] = Form(None),
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator)
):
    """Sube y procesa un documento PDF en el bucket indicado."""
    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Solo se admiten archivos PDF.")

    target_bucket = bucket_name.strip() if bucket_name else "general"

    # Verificar si el bucket existe; si no existe, crearlo automáticamente
    if not await milvus_client.bucket_exists(target_bucket):
        try:
            await milvus_client.create_bucket(
                name=target_bucket,
                content_type=content_type or "general",
                description=f"Bucket autogenerado para {target_bucket}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al inicializar el bucket '{target_bucket}': {e}")

    # Determinar el content_type efectivo
    resolved_content_type = content_type
    if not resolved_content_type:
        bucket_info = await milvus_client.get_bucket(target_bucket)
        resolved_content_type = bucket_info.get("content_type", "general") if bucket_info else "general"

    tmp_path = None
    try:
        # 1. Guardar temporalmente
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al guardar el archivo temporal: {e}")

        # 2. Extraer y dividir texto
        try:
            splitter = Splitter()
            docs = splitter.split_document(tmp_path)
            if not docs:
                raise HTTPException(status_code=400, detail="El documento PDF está vacío o no se pudo extraer texto.")
            for doc in docs:
                if 'metadata' not in doc:
                    doc['metadata'] = {}
                doc['metadata']["source_file"] = file.filename
                doc['metadata']["bucket"] = target_bucket
                doc['metadata']["content_type"] = resolved_content_type
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al extraer y dividir el documento: {e}")

        # 3. Generar embeddings
        try:
            text_chunks = [doc['text'] for doc in docs]
            vector_chunks = await embedding_generator.get_document_embedding(text_chunks)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al generar embeddings: {e}")

        # 4. Formatear e insertar en el bucket de Milvus
        try:
            data_to_insert = embedding_generator.format_database(
                text_chunks=docs,
                vector_chunks=vector_chunks,
                content_type=resolved_content_type
            )
            await milvus_client.upload_document(data=data_to_insert, collection_name=target_bucket)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al almacenar en la base de datos: {e}")

        return {
            "message": "Archivo cargado y procesado con éxito.",
            "bucket": target_bucket,
            "content_type": resolved_content_type,
            "chunks_procesados": len(docs)
        }

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/get-document")
async def get_document_endpoint(
    request: QueryRequest,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator),
    reranker: Reranker = Depends(get_reranker)
):
    """Busca fragmentos semánticamente similares dentro del bucket solicitado."""
    target_bucket = request.bucket_name.strip() if request.bucket_name else "general"

    if not await milvus_client.bucket_exists(target_bucket):
        raise HTTPException(status_code=404, detail=f"El bucket '{target_bucket}' no existe.")

    try:
        query_vector = await embedding_generator.get_query_embedding(request.query)
        
        results = await milvus_client.get_document(
            query_vector=query_vector,
            collection_name=target_bucket
        )
        
        if reranker is not None and len(results) > 0 and results[0]:
            final_results = reranker.rerank(request.query, results)
            msg = f"Búsqueda y reranking realizados en bucket '{target_bucket}'."
        else:
            final_results = results
            msg = f"Búsqueda realizada en bucket '{target_bucket}'."
        
        return {
            "message": msg,
            "bucket": target_bucket,
            "results": final_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la búsqueda: {e}")

@app.post("/generarRespuesta")
async def generar_respuesta_endpoint(
    request: QueryRequest,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator),
    reranker: Reranker = Depends(get_reranker)
):
    """Ejecuta el grafo evaluador RAG sobre el bucket especificado."""
    target_bucket = request.bucket_name.strip() if request.bucket_name else "general"

    if not await milvus_client.bucket_exists(target_bucket):
        raise HTTPException(status_code=404, detail=f"El bucket '{target_bucket}' no existe.")

    try:
        evaluator_graph = EvaluatorGraph(
            milvus_client=milvus_client,
            embedding_generator=embedding_generator,
            reranker=reranker
        )
        
        initial_state = {
            "query": request.query,
            "bucket_name": target_bucket,
            "context": "",
            "response": "",
            "feedback": "",
            "eval_status": "",
            "iteration": 0
        }
        
        final_state = await evaluator_graph.graph.ainvoke(initial_state)
        
        return {
            "message": "Respuesta evaluada y aprobada por el juez." if final_state["eval_status"] == "accepted" else "Límite de iteraciones alcanzado o sin contexto suficiente.",
            "bucket": target_bucket,
            "response": final_state["response"],
            "iteration": final_state.get("iteration", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la generación de respuesta: {e}")
