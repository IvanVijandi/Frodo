## Context
Actualmente se utiliza Milvus como base de datos vectorial para proyectos de RAG e Inteligencia Artificial, configurado mediante Docker Compose. Sin embargo, no existe una forma sencilla de visualizar y administrar las colecciones, los datos y la configuración interna de Milvus sin hacer uso de la API o herramientas de línea de comandos.

## Goals / Non-Goals

**Goals:**
- Proporcionar una interfaz gráfica de usuario (GUI) para interactuar con la instancia local de Milvus.
- Integrar la herramienta oficial "Attu" de Zilliz en la configuración existente de `docker-compose.yml`.
- Configurar la conectividad entre Attu y Milvus usando las variables de entorno recomendadas (`MILVUS_URL`).

**Non-Goals:**
- Configurar autenticación avanzada para Attu (ya que es para desarrollo local).
- Modificar la estructura de colecciones existentes en Milvus.
- Implementar la funcionalidad en entornos de producción en esta etapa.

## Decisions

**Decisión 1: Usar Attu oficial en Docker**
- *Alternativa*: Desarrollar un dashboard propio o usar otras herramientas genéricas.
- *Racional*: Attu (`zilliz/attu`) es la herramienta oficial diseñada específicamente para Milvus, soportando nativamente sus características, colecciones e indexado vectorial.

**Decisión 2: Configuración de red en Docker Compose**
- *Alternativa*: Ejecutar Attu como un contenedor aislado fuera de compose.
- *Racional*: Añadirlo al mismo `docker-compose.yml` asegura que se levanten juntos, compartan la misma red interna de Docker (`milvus`) y puedan comunicarse usando los nombres de los servicios (e.g. `http://standalone:19530` o la URL correspondiente a la instancia local de Milvus).

## Risks / Trade-offs

- *Riesgo*: Conflicto de puertos si el puerto 8000 ya está en uso.
  - *Mitigación*: Documentar que el puerto puede cambiarse en el archivo `docker-compose.yml` si fuese necesario.
- *Riesgo*: Consumo extra de memoria.
  - *Mitigación*: Attu es bastante liviano, el trade-off de recursos es mínimo comparado con los beneficios de observabilidad durante el desarrollo.
