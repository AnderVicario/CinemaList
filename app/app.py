from flask import Flask, jsonify
from flask_pymongo import PyMongo
import os

app = Flask(__name__)

# Función para leer la contraseña desde el archivo secreto
def read_mongo_password():
    with open('/run/secrets/mongodb_password', 'r') as file:
        return file.read().strip()  # Leer y eliminar cualquier espacio en blanco

# Configura la URI de MongoDB usando la contraseña leída
mongo_password = read_mongo_password()
app.config["MONGO_URI"] = f"mongodb://mongodb:{mongo_password}@mongodb:27017/movies?authSource=admin"
mongo = PyMongo(app)

# Ruta principal
@app.route('/')
def home():
    return "Bienvenido a la base de datos de películas"

# Ruta para ver los datos en /data
@app.route('/data')
def data():
    # Obtener todos los documentos de la colección 'movies'
    movies = list(mongo.db.movies.find({}, {"_id": 0}))  # Excluir el campo _id
    return jsonify(movies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)