## ADDED Requirements

### Requirement: Milvus Standalone Deployment
The system must provide a working Milvus standalone instance using Docker Compose.

#### Scenario: Service Connectivity
- **WHEN** the `docker compose up` command is executed
- **THEN** the `milvus-standalone` service should be healthy and listening on port `19530`.

### Requirement: Infrastructure Dependencies
Milvus must have its required dependencies (Etcd and MinIO) configured correctly.

#### Scenario: Dependency Health
- **WHEN** Milvus starts
- **THEN** it should be able to connect to the `etcd` service for metadata and `minio` service for storage.

### Requirement: Data Persistence
All data stored in Milvus, Etcd, and MinIO must persist across container restarts.

#### Scenario: Persistent Storage
- **WHEN** the containers are stopped and started again
- **THEN** the vector data and metadata should remain available.
