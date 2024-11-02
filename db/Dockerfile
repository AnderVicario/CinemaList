# Usar la imagen oficial de MongoDB como base
FROM mongo:latest

# Establecer variables de entorno para la autenticación de MongoDB
ENV MONGO_INITDB_ROOT_USERNAME=mongodb
ENV MONGO_INITDB_ROOT_PASSWORD=yourpassword
ENV MONGO_INITDB_DATABASE=movies

# Copiar el archivo CSV en el contenedor
COPY data.csv /docker-entrypoint-initdb.d/data.csv

# Copiar el script de importación
COPY init.sh /docker-entrypoint-initdb.d/init.sh
RUN chmod +x /docker-entrypoint-initdb.d/init.sh