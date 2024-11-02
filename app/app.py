from flask import Flask, jsonify, render_template, request
from flask_pymongo import PyMongo
import film_addons
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
    # Obtener el criterio de orden y el orden ascendente/descendente desde los argumentos de la URL
    sort_by = request.args.get('sort_by', 'Name')  # Orden por título como predeterminado
    order = request.args.get('order', 'asc')  # Orden ascendente por defecto

    # Definir el criterio de ordenamiento
    sort_order = 1 if order == 'asc' else -1

    # Obtener y ordenar los documentos según el criterio seleccionado
    movies = list(mongo.db.movies.find({}, {"_id": 0}).sort(sort_by, sort_order))

    return render_template('home.html', movies=movies, sort_by=sort_by, order=order)

# Ruta para ver cada pelicula
@app.route('/movies/<name>')
def movie_detail(name):
    try:
        # Convertir `movie_id` en ObjectId si es necesario y buscar la película en MongoDB
        movie = mongo.db.movies.find_one({"Name": name})
    except:
        movie = None

    # Si no se encuentra la película, mostrar un error 404
    if movie is None:
        abort(404)

    return render_template('movie.html', movie=movie)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)