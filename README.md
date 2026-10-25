# 🧙‍♂️ Frodo RAG — Reservorio Local de Conocimiento con IA Soberana

> **Frodo** es una plataforma de **Retrieval-Augmented Generation (RAG)** de arquitectura 100% local y soberana, diseñada para que cualquier usuario u organización disponga de su propio reservorio privado de información y una Inteligencia Artificial que responda consultas basándose **única y estrictamente en sus fuentes documentales**.

---

## 🌟 Visión y Filosofía

En un entorno digital donde los datos sensibles suelen terminar en servidores de terceros, **Frodo** plantea una alternativa libre de filtraciones:

1. **Privacidad y Soberanía Local**: Todos los componentes (modelos de lenguaje, bases vectoriales, almacenamiento relacional e interfaz de usuario) se ejecutan de manera local dentro de tu propia infraestructura mediante contenedores Docker.
2. **Generación Fundamentada (Zero Hallucination)**: La IA no "inventa" respuestas en el aire; busca primero fragmentos relevantes en los documentos indexados del usuario y razona basándose exclusivamente en esa evidencia (acompañando cada respuesta con sus citas y fuentes exactas).
3. **Ciclo de Auto-Evaluación (Evaluator-Optimizer Loop)**: La generación está gobernada por un grafo cíclico en **LangGraph** que evalúa si la respuesta generada satisface la pregunta y proviene realmente del contexto, corrigiendo o refinando la respuesta antes de mostrarla al usuario.

---

## 📦 ¿Qué es un "Bucket" en Frodo?

En el contexto de Frodo, un **Bucket** no es simplemente una carpeta de archivos; es un **Espacio Semántico de Conocimiento Aislado e Independiente**:

* **Aislamiento Temático**: Cada bucket (por ejemplo, *Finanzas*, *Legal*, *Proyectos*, *Cripto* o *General*) representa una colección vectorial propia en Milvus y un dominio temático delimitado.
* **Sin Contaminación Cruzada**: Cuando consultas a Frodo dentro de un bucket, el motor de búsqueda vectorial **únicamente recupera fragmentos de los documentos pertenecientes a ese espacio**. Un documento financiero jamás contaminará una consulta legal o técnica.
* **Hilos de Conversación Propios**: Las conversaciones y chats están asociados directamente al bucket activo en PostgreSQL. Al cambiar de bucket, tu historial de chat se mantiene ordenado y coherente con el área de trabajo en la que te encuentras.
* **Gestión Granular de Archivos**: Cada bucket dispone de una vista de administración particular donde puedes subir nuevos PDFs, visualizar los documentos indexados, ver el conteo de *chunks* (fragmentos semánticos) generados, eliminar archivos puntuales o suprimir el bucket completo con eliminación en cascada.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Función Principal |
| :--- | :--- | :--- |
| **Frontend** | **React 18 + Vite** | Interfaz web moderna, responsiva y minimalista en tonos claros y esmeralda (`Emerald / Mint Aesthetic`). |
| **Servidor Web & Proxy** | **Nginx (Alpine)** | Distribución de estáticos de React y *reverse proxy* hacia la API de FastAPI en el puerto `3000`. |
| **Backend API** | **FastAPI + Python 3.12** | API asíncrona de alto rendimiento, validaciones con Pydantic y gestión de dependencias con `uv`. |
| **Orquestación RAG** | **LangChain & LangGraph** | Pipeline de RAG agentico con grafo de estados cíclico (Retrieve $\rightarrow$ Generate $\rightarrow$ Evaluate $\rightarrow$ Optimize). |
| **Modelos de IA (LLM)** | **Ollama** | Motor de inferencia local para ejecutar modelos de vanguardia (Llama 3, Mistral, Qwen, DeepSeek) sin conexión a internet. |
| **Embeddings** | **Ollama Embeddings** | Generación de representaciones vectoriales locales (`nomic-embed-text`, etc.) con soporte configurable para Google Gemini. |
| **Reranking** | **FlashRank / Cross-Encoder** | Re-ordenamiento semántico de alta precisión sobre los fragmentos devueltos por la base vectorial. |
| **Base Vectorial** | **Milvus 2.4 Standalone** | Base de datos vectorial distribuida de alto rendimiento, asistida por **etcd** (metadatos) y **MinIO** (almacenamiento de objetos). |
| **GUI Vectorial** | **Attu (Milvus GUI)** | Panel visual para inspeccionar colecciones, vectores, métricas y esquemas en el puerto `8001`. |
| **Base de Datos Relacional** | **PostgreSQL 16 (Alpine)** | Persistencia de buckets, hilos de conversación y mensajes con UUIDs nativos y eliminación en cascada. Totalmente aislada en la red Docker interna. |
| **GUI Base de Datos** | **pgAdmin 4** | Panel web de administración para la base de datos PostgreSQL expuesto de forma segura en el puerto `5050`. |
| **Contenedores** | **Docker & Docker Compose** | Orquestación integral de microservicios con volúmenes persistentes y *healthchecks*. |

---

## 🏛️ Arquitectura del Sistema

La arquitectura está diseñada para desacoplar completamente la ingestión de documentos, la recuperación semántica, el ciclo de razonamiento del LLM y la persistencia de datos.

### Diagrama General de Componentes

```mermaid
flowchart TB
    subgraph Cliente["Cliente / Navegador"]
        UI["React Web App (Frodo UI)<br/>:3000"]
    end

    subgraph InfraProxy["Proxy & Ingress"]
        Nginx["Nginx Reverse Proxy<br/>:80 -> :3000"]
    end

    subgraph CoreBackend["Capa de Negocio (Backend)"]
        FastAPI["FastAPI App (:8000)<br/>Routers: Buckets, RAG, Conversaciones"]
        LangGraph["LangGraph Engine<br/>Evaluator-Optimizer Loop"]
    end

    subgraph VectorLayer["Capa Vectorial (RAG Retrieval)"]
        Milvus["Milvus Standalone (:19530)<br/>Colecciones por Bucket"]
        Attu["Attu Web GUI (:8001)"]
        Minio["MinIO (:9000)"]
        Etcd["etcd (:2379)"]
    end

    subgraph LocalAI["Capa de Inteligencia Artificial"]
        Ollama["Ollama Engine (:11434)<br/>LLM + Embeddings Locales"]
    end

    subgraph RelationalLayer["Capa de Persistencia y Auditoría"]
        Postgres["PostgreSQL 16 (:5432 interno)<br/>Tablas: buckets, conversaciones, mensajes"]
        pgAdmin["pgAdmin 4 (:5050)<br/>GUI de Administración"]
    end

    UI --> Nginx
    Nginx --> FastAPI
    FastAPI --> LangGraph
    LangGraph <--> Ollama
    LangGraph <--> Milvus
    FastAPI <--> Postgres
    Milvus --> Minio
    Milvus --> Etcd
    Attu --> Milvus
    pgAdmin --> Postgres
```

---

## 🔄 Flujos Operativos

### 1. Ingesta y Vectorización de Documentos
Cuando un usuario sube un archivo PDF a un bucket determinado:
1. El archivo se transmite a través del endpoint `POST /upload-pdf`.
2. El backend extrae el texto por páginas y lo divide en segmentos manejables (*chunks*) preservando metadatos del archivo de origen.
3. Se envían los chunks a **Ollama Embeddings** para generar sus vectores representativos.
4. Los vectores, texto y metadatos se indexan en la colección de **Milvus** correspondiente al bucket seleccionado.
5. El bucket queda actualizado en tiempo real con sus estadísticas de documentos y fragmentos.

```mermaid
sequenceDiagram
    autonumber
    actor Usuario
    participant UI as Frodo UI (React)
    participant API as FastAPI Backend
    participant Emb as Ollama (Embeddings)
    participant Milvus as Milvus DB
    participant PG as PostgreSQL

    Usuario->>UI: Sube documento PDF a Bucket
    UI->>API: POST /upload-pdf (FormData + bucket_name)
    API->>API: Extracción de texto y chunking semántico
    API->>Emb: Solicitar vectores de embeddings para los chunks
    Emb-->>API: Retorna listas de vectores numéricos
    API->>Milvus: Inserción de vectores + texto + metadatos
    API->>PG: Actualiza metadatos y timestamp del bucket
    API-->>UI: Confirmación de carga exitosa con total de chunks
    UI-->>Usuario: Muestra documento en la lista del bucket
```

---

### 2. Consulta RAG con Bucle de Auto-Evaluación (Evaluator-Optimizer)
Cuando el usuario envía una pregunta en el chat:
1. Se recupera el historial y se registra la pregunta en PostgreSQL bajo el `conversacion_id` del bucket activo.
2. La consulta ingresa al grafo **LangGraph**:
   - **Nodo Retrieval**: Genera el vector de la consulta y recupera en Milvus los fragmentos más afines del bucket.
   - **Nodo Rerank**: Un modelo clasificador reordena los fragmentos para priorizar la evidencia más precisa.
   - **Nodo Generate**: El LLM local (Ollama) redacta una respuesta apoyándose exclusivamente en el contexto.
   - **Nodo Evaluate**: Un evaluador estructurado analiza si la respuesta generada responde la pregunta sin alucinaciones. Si detecta desvíos, envía retroalimentación (*feedback*) al generador para corregir la respuesta de forma iterativa.
3. Al ser aceptada, la respuesta con sus citas y fuentes se almacena en PostgreSQL y se devuelve a la interfaz del usuario.

```mermaid
flowchart TD
    Inicio([Pregunta del Usuario]) --> CheckBucket[Verificar Bucket Activo]
    CheckBucket --> EmbedQuery[Generar Vector de Consulta]
    EmbedQuery --> Retrieve[Recuperar Chunks Relevantes en Milvus]
    Retrieve --> Rerank[Reranking Semántico de Fragmentos]
    Rerank --> GenLLM[LLM: Generar Respuesta con Contexto]
    GenLLM --> EvalLLM{Evaluador LLM:<br/>¿Es fiel al contexto?}
    
    EvalLLM -- "Rechazada (Feedback de alucinación)" --> GenLLM
    EvalLLM -- "Aprobada" --> PersistDB[Guardar Pregunta y Respuesta en PostgreSQL]
    PersistDB --> Fin([Mostrar Respuesta con Citas en Frodo UI])
```

---

## 📁 Estructura del Proyecto

```text
RAG/
└── MARIA/
    ├── docker-compose.yml       # Orquestación de todos los microservicios
    ├── Backend/
    │   ├── Dockerfile           # Imagen Docker de FastAPI con uv
    │   ├── pyproject.toml       # Especificación de dependencias (FastAPI, SQLAlchemy, LangGraph)
    │   ├── config.py            # Gestión centralizada de variables de entorno
    │   ├── FastApi/
    │   │   ├── main.py          # Punto de entrada de la API y ciclo de vida (Lifespan)
    │   │   ├── routers/         # Endpoints: buckets, conversaciones, rag
    │   │   └── use_cases/       # Lógica desacoplada de casos de uso
    │   ├── Langchain/
    │   │   ├── graph.py         # Grafo evaluador-optimizador de LangGraph
    │   │   ├── embbedings.py    # Generación y formateo de embeddings
    │   │   └── reranker.py      # Reordenamiento semántico con FlashRank
    │   ├── Milvus/
    │   │   └── main.py          # Cliente Milvus (creación de esquemas, búsqueda, borrado)
    │   └── Postgres/
    │       ├── connection.py    # Engine asíncrono SQLAlchemy (asyncpg) y sesión
    │       ├── init_db.py       # Inicialización automática de tablas en arranque
    │       ├── repository.py    # Operaciones CRUD para buckets, conversaciones y mensajes
    │       └── models/          # Modelos ORM: Bucket, Conversacion, Mensaje
    ├── Frontend/
    │   ├── Dockerfile           # Multi-stage build (Node 22 -> Nginx Alpine)
    │   ├── nginx.conf           # Configuración de Nginx y proxy reverso
    │   ├── index.html           # Documento HTML principal
    │   └── src/
    │       ├── components/      # BucketHubView, BucketDetailsView, ChatArea, Sidebar, etc.
    │       ├── hooks/           # useChatStorage (aislamiento por bucket)
    │       ├── services/        # Cliente API HTTP (Fetch)
    │       └── index.css        # Estilos globales y paleta de colores limpia
    └── README.md                # Esta documentación
```

---

## 🗄️ Modelo de Datos Relacional (PostgreSQL)

El almacenamiento relacional garantiza persistencia íntegra y trazabilidad con claves primarias UUID generadas por el backend:

```mermaid
erDiagram
    BUCKETS ||--o{ CONVERSACIONES : "contiene (1:N)"
    CONVERSACIONES ||--o{ MENSAJES : "posee (1:N)"

    BUCKETS {
        uuid id PK "Identificador único UUID"
        string nombre UK "Nombre único del bucket"
        string descripcion "Descripción temática"
        string content_type "Tipo de contenido o preset"
        timestamp fecha_creacion "Fecha de creación UTC"
        timestamp fecha_actualizacion "Última actualización"
    }

    CONVERSACIONES {
        uuid id PK "Identificador único UUID"
        uuid bucket_id FK "Referencia al bucket padre"
        string titulo "Título automático o personalizado"
        timestamp fecha_creacion "Fecha de inicio"
        timestamp fecha_actualizacion "Último mensaje recibido"
    }

    MENSAJES {
        uuid id PK "Identificador único UUID"
        uuid conversacion_id FK "Referencia a la conversación"
        string rol "user o assistant"
        text contenido "Texto del mensaje"
        jsonb fuentes "Citas, chunks y metadatos del PDF"
        timestamp fecha_creacion "Marca de tiempo UTC"
    }
```

> [!NOTE]
> Las relaciones cuentan con eliminación en cascada (`ON DELETE CASCADE`): eliminar un bucket borra automáticamente todas sus conversaciones y mensajes asociados, manteniendo la base de datos limpia de registros huérfanos.

---

## 🚀 Puesta en Marcha Rápida

### 1. Requisitos Previos
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución.
* [Ollama](https://ollama.ai/) instalado localmente en el host (o ejecutado vía contenedor).

### 2. Descargar los Modelos en Ollama
Asegúrate de contar con los modelos configurados para generación y embeddings:
```bash
# Modelo de lenguaje principal (generador y evaluador)
ollama pull llama3:latest

# Modelo de embeddings vectoriales
ollama pull nomic-embed-text:latest
```

### 3. Configurar Variables de Entorno
Crea o revisa el archivo `Backend/.env` (basado en `Backend/.env.example`):
```dotenv
# Proveedor LLM y Embeddings
LLM_PROVIDER=ollama
LLM_MODEL=llama3:latest
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text:latest
VECTOR_DIM=768
OLLAMA_URI=http://host.docker.internal:11434

# Milvus
MILVUS_URI=http://standalone:19530

# PostgreSQL (Persistencia Interna)
POSTGRES_USER=maria_user
POSTGRES_PASSWORD=maria_pass
POSTGRES_DB=maria_db
DATABASE_URL=postgresql+asyncpg://maria_user:maria_pass@postgres:5432/maria_db

# pgAdmin (GUI)
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin123
```

### 4. Iniciar Todos los Servicios con Docker Compose
Desde la carpeta raíz del proyecto (`MARIA/`):
```bash
docker compose up -d --build
```

---

## 🌐 Servicios y Puertos Disponibles

| Servicio | URL Local | Descripción |
| :--- | :--- | :--- |
| **Frodo Web App** | [http://localhost:3000](http://localhost:3000) | Aplicación web principal para gestionar buckets y chatear con tus documentos. |
| **pgAdmin 4 (GUI DB)** | [http://localhost:5050](http://localhost:5050) | Consola visual para consultar las tablas de PostgreSQL (`admin@admin.com` / `admin123`). |
| **Milvus Attu (GUI Vector)**| [http://localhost:8001](http://localhost:8001) | Dashboard visual para inspeccionar colecciones e índices vectoriales en Milvus. |
| **FastAPI Swagger Docs** | [http://localhost:3000/docs](http://localhost:3000/docs) | Documentación interactiva OpenAPI de todos los endpoints disponibles. |
| **Milvus Core API** | `localhost:19530` | Puerto gRPC/REST del motor Milvus. |
| **PostgreSQL 16** | *Interno Docker* | Base de datos relacional segura (sin puerto expuesto al host, accesible vía pgAdmin o red interna). |

---

## 🔒 Privacidad y Seguridad

* **Sin fuga de datos**: Tus documentos PDF se procesan en tu memoria local y residen en volúmenes Docker de tu propia máquina.
* **Red Segura**: PostgreSQL no publica el puerto `5432` hacia tu red local o internet; la comunicación se realiza exclusivamente a través de la red interna de Docker (`maria-postgres`).
* **Acceso Controlado**: Puedes administrar la base de datos de manera visual y segura a través de pgAdmin en `http://localhost:5050` con autenticación por credenciales locales.

---

## 📄 Licencia

Este proyecto se distribuye bajo fines de desarrollo, investigación y soberanía de datos personales y corporativos. Libre de usar y extender según las necesidades del usuario.

