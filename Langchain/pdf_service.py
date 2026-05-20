import os
import tempfile
from fastapi import UploadFile
from Langchain.Splitter import Splitter

async def process_pdf_upload(file: UploadFile):
    """
    Guarda el PDF temporalmente, extrae el texto y lo divide usando la clase Splitter.
    Retorna una lista de diccionarios con 'text' y 'metadata'.
    """
    # 1. Guardar archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        splitter = Splitter()
        split_docs = splitter.split_document(tmp_path)
        
        # Agregar metadatos útiles como el nombre original del archivo
        for doc in split_docs:
            doc['metadata']["source_file"] = file.filename

        return split_docs

    finally:
        # Limpiar el archivo temporal
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
