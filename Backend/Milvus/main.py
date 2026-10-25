import datetime
import re
from pymilvus import MilvusClient, DataType, AsyncMilvusClient

try:
    from config import conf 
except ModuleNotFoundError:
    from Backend.config import conf

REGISTRY_COLLECTION = "_buckets_registry"
DEFAULT_VECTOR_DIM = getattr(conf, "VECTOR_DIM", 768)

def normalize_bucket_name(name: str) -> str:
    """Normaliza un nombre de bucket a caracteres alfanuméricos en minúsculas y guiones bajos."""
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', name.strip().lower())
    clean = re.sub(r'_+', '_', clean).strip('_')
    if not clean or not clean[0].isalpha() and clean[0] != '_':
        clean = f"bucket_{clean}"
    return clean

class Async_Milvus_Client:
    """Clase para el cliente asíncrono de Milvus con soporte de Buckets y Metadatos."""
    
    def __init__(self):
        self.client = AsyncMilvusClient(uri=conf.MILVUS_URI, db_name="MARIA")
        self.sync_client = MilvusClient(uri=conf.MILVUS_URI, db_name="MARIA")

    async def _ensure_registry(self):
        """Asegura que la colección interna de registro _buckets_registry exista en Milvus."""
        try:
            collections = await self.client.list_collections()
            if REGISTRY_COLLECTION not in collections:
                reg_schema = MilvusClient.create_schema(
                    auto_id=False,
                    enable_dynamic_field=True,
                )
                reg_schema.add_field(field_name="bucket_name", datatype=DataType.VARCHAR, max_length=128, is_primary=True)
                reg_schema.add_field(field_name="content_type", datatype=DataType.VARCHAR, max_length=100)
                reg_schema.add_field(field_name="description", datatype=DataType.VARCHAR, max_length=1000)
                reg_schema.add_field(field_name="created_at", datatype=DataType.VARCHAR, max_length=64)
                reg_schema.add_field(field_name="metadata", datatype=DataType.JSON)

                index_params = self.sync_client.prepare_index_params()
                index_params.add_index(
                    field_name="bucket_name",
                    index_type="INVERTED"
                )

                await self.client.create_collection(
                    collection_name=REGISTRY_COLLECTION,
                    schema=reg_schema,
                    index_params=index_params
                )
                try:
                    await self.client.load_collection(collection_name=REGISTRY_COLLECTION)
                except Exception:
                    pass
        except Exception as e:
            print(f"Nota en _ensure_registry: {e}")

    async def bucket_exists(self, bucket_name: str) -> bool:
        """Verifica si la colección de un bucket existe en Milvus."""
        clean_name = normalize_bucket_name(bucket_name)
        collections = await self.client.list_collections()
        return clean_name in collections

    async def create_bucket(
        self,
        name: str,
        content_type: str = "general",
        description: str = "",
        metadata: dict = None,
        dim: int = DEFAULT_VECTOR_DIM
    ) -> dict:
        """
        Crea un nuevo bucket (colección en Milvus) y registra sus metadatos.
        """
        clean_name = normalize_bucket_name(name)
        if clean_name == REGISTRY_COLLECTION:
            raise ValueError(f"El nombre '{clean_name}' está reservado para el sistema.")

        await self._ensure_registry()

        collections = await self.client.list_collections()
        if clean_name not in collections:
            schema = MilvusClient.create_schema(
                auto_id=True,
                enable_dynamic_field=True,
            )
            schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
            schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=dim)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="source_file", datatype=DataType.VARCHAR, max_length=255)
            schema.add_field(field_name="content_type", datatype=DataType.VARCHAR, max_length=100)
            schema.add_field(field_name="metadata", datatype=DataType.JSON)

            index_params = self.sync_client.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )
            index_params.add_index(
                field_name="content_type",
                index_type="INVERTED"
            )

            await self.client.create_collection(
                collection_name=clean_name,
                schema=schema,
                index_params=index_params
            )
            await self.client.load_collection(collection_name=clean_name)

        # Registrar o actualizar metadatos en _buckets_registry
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        reg_data = [{
            "bucket_name": clean_name,
            "content_type": content_type or "general",
            "description": description or "",
            "created_at": created_at,
            "metadata": metadata or {}
        }]
        await self.client.upsert(
            collection_name=REGISTRY_COLLECTION,
            data=reg_data
        )

        return {
            "name": clean_name,
            "content_type": content_type or "general",
            "description": description or "",
            "created_at": created_at,
            "metadata": metadata or {}
        }

    async def list_buckets(self) -> list[dict]:
        """
        Lista todos los buckets registrados junto con sus metadatos y conteo de fragmentos.
        """
        await self._ensure_registry()
        # 1. Obtener colecciones físicas en Milvus
        physical_collections = set(await self.client.list_collections())
        physical_collections.discard(REGISTRY_COLLECTION)

        # 2. Obtener metadatos guardados en _buckets_registry
        registered_buckets = {}
        try:
            results = await self.client.query(
                collection_name=REGISTRY_COLLECTION,
                filter='bucket_name != ""',
                output_fields=["bucket_name", "content_type", "description", "created_at", "metadata"]
            )
            for item in results:
                registered_buckets[item["bucket_name"]] = item
        except Exception as e:
            print(f"Nota al consultar {REGISTRY_COLLECTION}: {e}")

        bucket_list = []
        for b_name in physical_collections:
            meta_info = registered_buckets.get(b_name, {})
            
            # Obtener conteo de entidades si es posible
            total_chunks = 0
            try:
                stats = await self.client.get_collection_stats(collection_name=b_name)
                total_chunks = stats.get("row_count", 0)
            except Exception:
                pass

            bucket_list.append({
                "name": b_name,
                "content_type": meta_info.get("content_type", "general"),
                "description": meta_info.get("description", ""),
                "created_at": meta_info.get("created_at", ""),
                "metadata": meta_info.get("metadata", {}),
                "total_chunks": total_chunks
            })

        # Ordenar alfabéticamente dejando 'general' al inicio
        bucket_list.sort(key=lambda x: (x["name"] != "general", x["name"]))
        return bucket_list

    async def get_bucket(self, name: str) -> dict | None:
        """Obtiene la información y metadatos de un bucket específico."""
        await self._ensure_registry()
        clean_name = normalize_bucket_name(name)
        if not await self.bucket_exists(clean_name):
            return None

        try:
            results = await self.client.query(
                collection_name=REGISTRY_COLLECTION,
                filter=f'bucket_name == "{clean_name}"',
                output_fields=["bucket_name", "content_type", "description", "created_at", "metadata"]
            )
            if results:
                info = results[0]
            else:
                info = {
                    "bucket_name": clean_name,
                    "content_type": "general",
                    "description": "",
                    "created_at": "",
                    "metadata": {}
                }
        except Exception:
            info = {
                "bucket_name": clean_name,
                "content_type": "general",
                "description": "",
                "created_at": "",
                "metadata": {}
            }

        try:
            stats = await self.client.get_collection_stats(collection_name=clean_name)
            info["total_chunks"] = stats.get("row_count", 0)
        except Exception:
            info["total_chunks"] = 0

        info["name"] = info.pop("bucket_name", clean_name)
        return info

    async def delete_bucket(self, name: str) -> bool:
        """Elimina un bucket (su colección vectorial y su registro de metadatos)."""
        clean_name = normalize_bucket_name(name)
        if clean_name == "general":
            raise ValueError("No se puede eliminar el bucket principal 'general'.")
        if clean_name == REGISTRY_COLLECTION:
            raise ValueError(f"No se puede eliminar la colección del sistema '{REGISTRY_COLLECTION}'.")

        # Eliminar colección física
        if await self.bucket_exists(clean_name):
            await self.client.drop_collection(collection_name=clean_name)

        # Eliminar del registro
        try:
            await self.client.delete(
                collection_name=REGISTRY_COLLECTION,
                ids=[clean_name]
            )
        except Exception as e:
            print(f"Nota al borrar registro de {clean_name}: {e}")

        return True

    async def get_document(
        self,
        query_vector: list[float],
        collection_name: str = "general",
        limit: int = 10,
        filter: str = None
    ) -> list[dict]:
        """Devuelve los chunks más similares a la query dentro de la colección/bucket especificado."""
        clean_name = normalize_bucket_name(collection_name)
        
        results = await self.client.search(
            collection_name=clean_name,
            data=[query_vector],
            anns_field="vector",
            search_params={"metric_type": "COSINE"},
            limit=limit,
            filter=filter,
            output_fields=["id", "text", "source_file", "content_type", "metadata"]
        )
        # En pymilvus search devuelve una lista por cada vector de consulta en data.
        # Desempaquetamos results[0] para retornar una lista plana de hits.
        if results and isinstance(results, list) and len(results) > 0 and isinstance(results[0], list):
            return results[0]
        return results or []

    async def upload_document(self, data: list[dict], collection_name: str = "general"):
        """Inserta chunks de documentos en el bucket especificado."""
        clean_name = normalize_bucket_name(collection_name)
        insert_results = await self.client.insert(
            collection_name=clean_name,
            data=data
        )
        return insert_results

    async def list_documents(self, name: str) -> list[dict]:
        """Obtiene la lista de documentos agrupados por archivo fuente en este bucket."""
        clean_name = normalize_bucket_name(name)
        if not await self.bucket_exists(clean_name):
            return []
        try:
            results = await self.client.query(
                collection_name=clean_name,
                filter="id >= 0",
                output_fields=["id", "source_file", "content_type", "metadata"],
                limit=16384
            )
            docs_map = {}
            for r in results:
                sf = r.get("source_file") or "desconocido"
                if sf not in docs_map:
                    docs_map[sf] = {
                        "filename": sf,
                        "chunks_count": 0,
                        "content_type": r.get("content_type", "general"),
                    }
                docs_map[sf]["chunks_count"] += 1
            return list(docs_map.values())
        except Exception as e:
            print(f"Nota al listar documentos de {clean_name}: {e}")
            return []

    async def delete_document(self, name: str, filename: str) -> bool:
        """Elimina todos los fragmentos asociados a un archivo dentro del bucket especificado."""
        clean_name = normalize_bucket_name(name)
        if not await self.bucket_exists(clean_name):
            return False
        try:
            await self.client.delete(
                collection_name=clean_name,
                filter=f'source_file == "{filename}"'
            )
            return True
        except Exception as e:
            print(f"Error al eliminar documento {filename} de {clean_name}: {e}")
            return False
