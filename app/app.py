from flask import Flask, jsonify, render_template, request, abort, url_for, redirect
from flask_pymongo import PyMongo
from bson.son import SON
from bson import ObjectId
import utilities
import os


app = Flask(__name__)

# Configurar base de datos
def read_mongo_password():
    with open('/run/secrets/mongodb_password', 'r') as file:
        return file.read().strip()

mongo_password = read_mongo_password()
app.config["MONGO_URI"] = f"mongodb://mongodb:{mongo_password}@mongodb:27017/movies?authSource=admin"
mongo = PyMongo(app)


def clean_votes(votes):
    if isinstance(votes, int):  # Si ya es un entero, devuelve el valor
        return votes
    if votes == 'No Votes':
        return 0  # O manejarlo de otra manera
    return int(votes.replace(',', ''))


# Ruta principal
@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'Name')
    order = request.args.get('order', 'asc')

    sort_order = 1 if order == 'asc' else -1

    if sort_by == 'Votes':
        movies = list(mongo.db.movies.find({}, {"_id": 0}))
        # Ordenar usando la función de limpieza
        movies.sort(key=lambda x: clean_votes(x[sort_by]), reverse=(sort_order == -1))
    else:
        movies = list(mongo.db.movies.find({}, {"_id": 0}).sort(sort_by, sort_order))

    return render_template('home.html', movies=movies, sort_by=sort_by, order=order)


# Ruta para ver cada pelicula
@app.route('/movies/name=<path:name>')
def movie_detail(name):
    movie = mongo.db.movies.find_one({"Name": name})

    if movie is None:
        movie = mongo.db.movies.find_one({"Name": int(name)})

    if movie is None:
        abort(404)

    url, description = utilities.obtener_datos_pelicula(str(movie["Name"]), str(movie["Date"]))
    return render_template('movie.html', movie=movie, url=url, description=description)


# Ruta para añadir rating
@app.route('/submit_value', methods=['POST'])
def submit_value():
    input_value = request.form.get('input_value')
    movie_id = request.form.get('movie_id')

    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    if movie:
        # Manejo especial para 'No Votes' y 'No Rate'
        votes_str = movie.get("Votes", "0")
        rate_str = movie.get("Rate", "0")

        if votes_str == 'No Votes':
            votes = 0
        else:
            votes = int(str(votes_str).replace(',', ''))

        if rate_str == 'No Rate':
            rate = 0.0  # O puedes establecer otro valor predeterminado si prefieres
        else:
            rate = float(rate_str)

        new_votes = votes + 1
        new_rate = (votes * rate + int(input_value)) / new_votes if new_votes > 0 else float(input_value)
        new_rate = round(new_rate, 1)

        new_votes_formatted = f"{new_votes:,}"

        mongo.db.movies.update_one(
            {"_id": ObjectId(movie_id)},
            {"$set": {"Rate": new_rate, "Votes": new_votes_formatted}}
        )

    return redirect(url_for('home'))

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)