## 1. Modificar docker-compose.yml

- [x] 1.1 Revisar el nombre del servicio de Milvus y la red en `docker-compose.yml` para asegurar la conectividad correcta.
- [x] 1.2 Agregar la definición del servicio `attu` bajo la sección `services`, usando la imagen oficial `zilliz/attu:v2.4` o superior.
- [x] 1.3 Configurar la variable de entorno `MILVUS_URL` para que apunte a la instancia local de Milvus.
- [x] 1.4 Exponer el puerto `8000:3000` (el contenedor de Attu escucha en el 3000).
- [x] 1.5 Asignar la misma red de Docker al servicio `attu` que la que usa Milvus.

## 2. Pruebas y Verificación

- [ ] 2.1 Levantar los servicios con `docker compose up -d` o equivalente.
- [ ] 2.2 Revisar los logs de Attu para confirmar que la conexión inicial con Milvus ha sido exitosa.
