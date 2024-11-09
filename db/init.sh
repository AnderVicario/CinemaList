#!/bin/bash

# Esperar a que MongoDB esté listo
sleep 10

# Eliminar duplicados del CSV basados en la columna Name
# Asumiendo que la primera línea es el encabezado
head -n 1 /docker-entrypoint-initdb.d/data.csv > /tmp/unique_data.csv
tail -n +2 /docker-entrypoint-initdb.d/data.csv | sort -t',' -k1,1 -u >> /tmp/unique_data.csv

# Ejecutar el comando mongoimport para importar el archivo CSV a la base de datos
mongoimport --host localhost --db "$MONGO_INITDB_DATABASE" --collection movies \
  --type csv --file /tmp/unique_data.csv --headerline \
  --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin

# Limpiar el archivo temporal
rm /tmp/unique_data.csv