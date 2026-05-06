## ADDED Requirements

### Requirement: Attu UI Service
El sistema SHALL incluir el servicio `attu` en el archivo `docker-compose.yml` para proveer una interfaz gráfica de administración de Milvus.

#### Scenario: Contenedor se inicia correctamente
- **WHEN** se ejecuta el comando `docker-compose up`
- **THEN** el servicio de Attu se levanta y es accesible en el puerto expuesto (por defecto 8000)

### Requirement: Attu to Milvus Connection
El servicio `attu` SHALL estar configurado para conectarse a la instancia local de Milvus.

#### Scenario: Attu visualiza los datos
- **WHEN** el usuario accede a la interfaz de Attu en el navegador
- **THEN** el usuario puede visualizar las colecciones y configuración de la instancia de Milvus configurada
