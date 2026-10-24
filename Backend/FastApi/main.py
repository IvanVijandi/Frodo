import sys
import os

# Asegurar que el directorio de Backend (o /app en Docker) esté en sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException, File, Form, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
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
    try:
        setup_database()
    except Exception as e:
        print(f"Advertencia durante setup_database en Milvus: {e}")
    
    app.state.reranker = Reranker() if conf.RERANKER_PROVIDER.lower() != "none" else None
    app.state.embedding_generator = EmbeddingGenerator()
    app.state.milvus_client = Async_Milvus_Client()
    yield

tags_metadata = [
    {
        "name": "Buckets",
        "description": "Operaciones para crear, listar, inspeccionar y eliminar colecciones vectoriales temáticas en Milvus.",
    },
    {
        "name": "Ingesta",
        "description": "Extracción de texto, fragmentación (chunking), generación de embeddings e indexación de PDFs.",
    },
    {
        "name": "RAG & Búsqueda",
        "description": "Búsqueda vectorial semántica con reranking y generación de respuestas fundamentadas evaluadas con LangGraph.",
    },
    {
        "name": "Sistema",
        "description": "Comprobación de estado y disponibilidad del servicio.",
    },
]

app = FastAPI(
    title="MARIA - RAG API & Knowledge Engine",
    description="""
# 🤖 MARIA - Asistente RAG Multi-Bucket

Bienvenido a la documentación interactiva Swagger de la API de **MARIA**.
Esta plataforma permite:
* **Crear y administrar Buckets**: Organiza tus documentos en colecciones vectoriales separadas según su tipo de contenido (*legal*, *financiero*, *técnico*, *general*).
* **Ingesta de Documentos PDF**: Sube archivos PDF para ser procesados, divididos en fragmentos e indexados en Milvus.
* **Consultas RAG Inteligentes**: Realiza preguntas dirigidas a un bucket específico con recuperación semántica, reranking opcional y evaluación de alucinaciones con LangGraph.
    """,
    version="2.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

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
    name: str = Field(..., description="Nombre del bucket (ej: 'legal_docs', 'finanzas_2026')", example="legal_docs")
    content_type: str = Field("general", description="Categoría temática del contenido", example="legal")
    description: Optional[str] = Field("", description="Descripción del propósito del bucket", example="Contratos y normativas legales")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Metadatos adicionales en formato clave-valor", example={"tags": ["contratos", "2026"]})

class QueryRequest(BaseModel):
    query: str = Field(..., description="Pregunta o consulta del usuario", example="¿Cuáles son las cláusulas de rescisión del contrato?")
    bucket_name: Optional[str] = Field("general", description="Nombre del bucket sobre el que realizar la búsqueda", example="general")

## Health Check
@app.get(
    "/",
    tags=["Sistema"],
    summary="Health check del servicio",
    description="Verifica que la API esté activa y respondiendo correctamente."
)
async def ok():
    return {"message": "ok", "service": "MARIA Backend", "version": "2.0.0"}

# ==============================================================================
# Endpoints de Gestión de Buckets
# ==============================================================================

@app.get(
    "/buckets",
    tags=["Buckets"],
    summary="Listar todos los buckets registrados",
    description="Devuelve la lista de todos los buckets con su tipo de contenido, descripción, fecha de creación y conteo de fragmentos indexados."
)
async def list_buckets(
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
    try:
        buckets = await milvus_client.list_buckets()
        return {"buckets": buckets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar buckets: {e}")

@app.post(
    "/buckets",
    tags=["Buckets"],
    summary="Crear un nuevo bucket",
    description="Crea una nueva colección vectorial en Milvus con índice optimizado y registra sus metadatos de tipo de contenido."
)
async def create_bucket(
    request: BucketCreateRequest,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
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

@app.get(
    "/buckets/{bucket_name}",
    tags=["Buckets"],
    summary="Obtener detalles de un bucket",
    description="Consulta la información detallada, metadatos y cantidad de chunks de un bucket por su nombre."
)
async def get_bucket(
    bucket_name: str,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
    bucket_info = await milvus_client.get_bucket(bucket_name)
    if not bucket_info:
        raise HTTPException(status_code=404, detail=f"El bucket '{bucket_name}' no existe.")
    return {"bucket": bucket_info}

@app.delete(
    "/buckets/{bucket_name}",
    tags=["Buckets"],
    summary="Eliminar un bucket",
    description="Elimina la colección física en Milvus y su registro de metadatos. El bucket por defecto 'general' está protegido."
)
async def delete_bucket(
    bucket_name: str,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client)
):
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

@app.post(
    "/upload-file",
    tags=["Ingesta"],
    summary="Subir e indexar un documento PDF en un bucket",
    description="Recibe un archivo PDF, divide su contenido en fragmentos textuales, genera sus embeddings vectoriales y los almacena en el bucket seleccionado."
)
async def upload_file(
    file: UploadFile = File(..., description="Archivo PDF para procesar e indexar"),
    bucket_name: str = Form("general", description="Bucket de destino para almacenar el documento"),
    content_type: Optional[str] = Form(None, description="Tipo de contenido opcional (si se omite, hereda el del bucket)"),
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator)
):
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

@app.post(
    "/get-document",
    tags=["RAG & Búsqueda"],
    summary="Búsqueda vectorial semántica en un bucket",
    description="Calcula el embedding de la consulta, recupera los fragmentos más cercanos en el bucket y aplica reranker si está disponible."
)
async def get_document_endpoint(
    request: QueryRequest,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator),
    reranker: Reranker = Depends(get_reranker)
):
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

@app.post(
    "/generarRespuesta",
    tags=["RAG & Búsqueda"],
    summary="Generar respuesta RAG evaluada sobre un bucket",
    description="Ejecuta el grafo LangGraph (EvaluatorGraph): recupera contexto del bucket, genera respuesta y la somete a evaluación del juez para evitar alucinaciones."
)
async def generar_respuesta_endpoint(
    request: QueryRequest,
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator),
    reranker: Reranker = Depends(get_reranker)
):
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
