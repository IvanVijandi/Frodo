## Context

The project currently uses Docker Compose to manage local services, with `ollama` as the only active service. To support vector search capabilities, we need to integrate Milvus Standalone.

## Goals / Non-Goals

**Goals:**
- Add Milvus Standalone service to the existing `docker-compose.yml`.
- Add required dependencies: Etcd (metadata) and MinIO (object storage).
- Configure persistent volumes for all services to ensure data durability.
- Expose the necessary ports for external connectivity (19530 for Milvus).

**Non-Goals:**
- Setting up a Milvus Cluster (out of scope for local development).
- Installing Milvus Attu (management UI) - focus is on the core database service.
- Performance tuning for production environments.

## Decisions

- **Milvus Version**: Use `milvusdb/milvus:latest` (stable standalone).
- **Storage**: Use MinIO for object storage and Etcd for metadata storage, as required by Milvus Standalone.
- **Persistent Volumes**: 
    - `etcd_data` for Etcd metadata.
    - `minio_data` for MinIO object storage.
    - `milvus_data` for Milvus data files.
- **Network**: All services will run on the default Docker Compose network to allow easy inter-service communication.
- **Environment Variables**: Use standard recommended configurations for standalone mode.

## Risks / Trade-offs

- **System Resources**: Milvus Standalone with its dependencies is resource-intensive. It may significantly increase CPU and RAM usage on the host machine.
- **Complexity**: Adding three new services increases the complexity of the local development environment and potential failure points during startup.
- **Startup Sequence**: Milvus depends on Etcd and MinIO being ready. While `depends_on` handles container startup order, Milvus may still experience initial connection retries until the dependencies are fully initialized.
