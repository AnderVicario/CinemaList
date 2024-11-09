# Usar la imagen oficial de MongoDB como base
FROM mongo:4.4

# Copiar el archivo CSV en el contenedor
COPY data.csv /docker-entrypoint-initdb.d/data.csv

# Copiar el script de importación
COPY init.sh /docker-entrypoint-initdb.d/init.sh
RUN chmod +x /docker-entrypoint-initdb.d/init.sh