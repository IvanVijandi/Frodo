## 1. Dockerfile Creation

- [x] 1.1 Crear el archivo `Dockerfile` en la raíz del proyecto, basado en la imagen `python:3.10-slim`.
- [x] 1.2 Configurar el `WORKDIR` y copiar el archivo `requeriments.txt` dentro del contenedor.
- [x] 1.3 Agregar el comando `RUN pip install -r requeriments.txt` para instalar las dependencias.
- [x] 1.4 Exponer el puerto `8000` y configurar el comando de inicio `CMD ["uvicorn", "FastApi.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]`.

## 2. Docker Compose Integration

- [x] 2.1 Modificar `docker-compose.yml` para añadir el servicio `backend`.
- [x] 2.2 Configurar el servicio `backend` para usar `build: .` y montar el volumen local `.:/app`.
- [x] 2.3 Mapear los puertos `"8000:8000"` para el servicio `backend`.
- [x] 2.4 Agregar las variables de entorno `MILVUS_URI=http://milvus-standalone:19530` y `OLLAMA_URI=http://ollama:11434` en el servicio `backend`.
- [x] 2.5 Configurar el `depends_on` del servicio `backend` para que dependa de `milvus-standalone` y `ollama`.

## 3. Configuration Update

- [x] 3.1 Revisar `config.py` o los archivos `.env` locales para asegurar que den prioridad a las variables inyectadas por Docker (usando `os.getenv`).

## 4. Verification

- [x] 4.1 Ejecutar `docker-compose up --build -d` para verificar que la imagen del backend compila correctamente y el contenedor arranca.
- [x] 4.2 Probar un endpoint localmente a través de `http://localhost:8000/docs` comprobando la comunicación interna.
