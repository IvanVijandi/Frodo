## Why

The project requires a high-performance vector database to store and query sign language embeddings and other vectorized data. Adding Milvus standalone provides a robust solution for these vector search capabilities within the local development environment.

## What Changes

- Integration of Milvus standalone into the `docker-compose.yml` file.
- Addition of required infrastructure services for Milvus:
    - **Etcd**: Used for metadata storage and cluster coordination.
    - **MinIO**: Used for object storage (logs, data files, index files).
- Configuration of persistent volumes for all new services.
- Setup of necessary environment variables and networking.

## Capabilities

### New Capabilities
- `milvus-infrastructure`: Provisioning and management of the Milvus vector database and its dependencies (Etcd, MinIO) via Docker Compose.

### Modified Capabilities
- (None)

## Impact

- **docker-compose.yml**: Modified to include three new services (`milvus`, `etcd`, `minio`).
- **Resource Usage**: Significant increase in memory and disk usage to support Milvus and its dependencies.
- **Local Development**: Developers will need to pull new images and restart the compose stack to access the vector database.
