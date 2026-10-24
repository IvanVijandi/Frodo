## 1. Infrastructure Preparation

- [x] 1.1 Add persistent volumes for Etcd, MinIO, and Milvus to the `volumes` section of `docker-compose.yml`.
- [x] 1.2 Define the `etcd` service in `docker-compose.yml` with necessary health checks and volumes.
- [x] 1.3 Define the `minio` service in `docker-compose.yml` with storage configuration and health checks.

## 2. Milvus Integration

- [x] 2.1 Add the `milvus-standalone` service to `docker-compose.yml`, configuring it to depend on `etcd` and `minio`.
- [x] 2.2 Configure environment variables for Milvus to connect to its dependencies.
- [x] 2.3 Map port `19530` for Milvus client connections.

## 3. Verification

- [ ] 3.1 Start the services using `docker compose up -d`.
- [ ] 3.2 Verify all services (`etcd`, `minio`, `milvus`) are healthy and running.
