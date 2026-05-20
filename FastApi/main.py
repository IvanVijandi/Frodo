from fastapi import FastAPI, UploadFile, HTTPException, File, Depends, Request
from contextlib import asynccontextmanager
import tempfile
import os
import time

from Langchain.embbedings import EmbeddingGenerator
from Langchain.Splitter import Splitter
from Langchain.Reranker import Reranker
from Milvus.main import Async_Milvus_Client

##Lifespan. Se encarga de inicializar y cerrar recursos al iniciar y cerrar el servidor.
@asynccontextmanager
async def lifespan(app: FastAPI):
    ##Instancias de las clases pesadas guardadas en app.state
    app.state.reranker = Reranker()
    app.state.embedding_generator = EmbeddingGenerator()  ## Lee EMBEDDING_PROVIDER del .env
    app.state.milvus_client = Async_Milvus_Client()
    yield

app = FastAPI(lifespan=lifespan)

# Dependencias para inyectar en los endpoints
def get_milvus_client(request: Request):
    return request.app.state.milvus_client

def get_embedding_generator(request: Request):
    return request.app.state.embedding_generator

##Para probar que el servidor esta corriendo
@app.get("/")
async def ok():
    return {"message": "ok"}

@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator)
):
    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Solo se admiten archivos PDF.")

    tmp_path = None
    try:
        # 1. Guardar el archivo temporalmente
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al guardar el archivo temporal: {e}")

        # 2. Extraer y dividir texto usando Splitter
        try:
            splitter = Splitter()
            docs = splitter.split_document(tmp_path)
            if not docs:
                raise HTTPException(status_code=400, detail="El documento PDF está vacío o no se pudo extraer texto.")
            for doc in docs:
                doc['metadata']["source_file"] = file.filename
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

        # 4. Formatear e insertar en Milvus
        try:
            pdf_id = int(time.time())
            data_to_insert = embedding_generator.format_database(docs, vector_chunks, pdf_id)
            await milvus_client.upload_document(data=data_to_insert, collection_name="documentos")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al almacenar en la base de datos: {e}")

        return {
            "message": "Archivo cargado y procesado con éxito.",
            "chunks_procesados": len(docs),
            "pdf_id": pdf_id
        }

    finally:
        # Limpiar el archivo temporal
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
