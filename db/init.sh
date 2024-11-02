#!/bin/bash

# Esperar a que MongoDB esté listo
sleep 10

# Ejecutar el comando mongoimport para importar el archivo CSV a la base de datos
mongoimport --host localhost --db "$MONGO_INITDB_DATABASE" --collection movies \
  --type csv --file /docker-entrypoint-initdb.d/data.csv --headerline \
  --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin