# Etapa 1: Compilación de la aplicación React con Vite
FROM node:22-alpine AS build

WORKDIR /app

# Instalar dependencias primero para optimizar la caché de capas Docker
COPY package*.json ./
RUN npm install

# Copiar el código fuente y construir los estáticos
COPY . .
RUN npm run build

# Etapa 2: Servidor Web Nginx para estáticos y reverse proxy
FROM nginx:alpine

# Limpiar archivos por defecto de nginx
RUN rm -rf /usr/share/nginx/html/*

# Copiar la salida compilada de React
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar la configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

