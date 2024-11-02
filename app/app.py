from flask import Flask, jsonify, render_template, request, abort
from flask_pymongo import PyMongo
import film_addons
import os


app = Flask(__name__)

# Configurar base de datos
def read_mongo_password():
    with open('/run/secrets/mongodb_password', 'r') as file:
        return file.read().strip()

mongo_password = read_mongo_password()
app.config["MONGO_URI"] = f"mongodb://mongodb:{mongo_password}@mongodb:27017/movies?authSource=admin"
mongo = PyMongo(app)


# Ruta principal
@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'Name')
    order = request.args.get('order', 'asc')

    sort_order = 1 if order == 'asc' else -1

    movies = list(mongo.db.movies.find({}, {"_id": 0}).sort(sort_by, sort_order))

    return render_template('home.html', movies=movies, sort_by=sort_by, order=order)


# Ruta para ver cada pelicula
@app.route('/movies/<name>')
def movie_detail(name):
        
    movie = mongo.db.movies.find_one({"Name": name})
    url = film_addons.obtener_portada_pelicula(str(movie["Name"]), str(movie["Date"]))

    if movie is None:
        abort(404)

    return render_template('movie.html', movie=movie, url=url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)