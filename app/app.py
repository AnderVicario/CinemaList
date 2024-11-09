from flask import Flask, render_template, request, abort, url_for, redirect, session
from flask_pymongo import PyMongo
from bson.son import SON
from bson import ObjectId
from datetime import timedelta
import utilities
import os


app = Flask(__name__)

# Configurar base de datos
def read_mongo_password():
    with open('/run/secrets/mongodb_password', 'r') as file:
        return file.read().strip()

mongo_password = read_mongo_password()
app.secret_key = mongo_password
app.permanent_session_lifetime = timedelta(minutes=10)
app.config["MONGO_URI"] = f"mongodb://mongodb:{mongo_password}@mongodb:27017/movies?authSource=admin"
mongo = PyMongo(app)


def clean_votes(votes):
    if isinstance(votes, int):
        return votes
    if votes == 'No Votes':
        return 0
    return int(votes.replace(',', ''))


# Ruta principal
@app.route('/')
def home():
    is_logged_in = 'user_id' in session
    sort_by = request.args.get('sort_by', 'Name')
    order = request.args.get('order', 'asc')

    sort_order = 1 if order == 'asc' else -1

    if sort_by == 'Votes':
        movies = list(mongo.db.movies.find({}, {"_id": 0}))
        # Ordenar usando la función de limpieza
        movies.sort(key=lambda x: clean_votes(x[sort_by]), reverse=(sort_order == -1))
    else:
        movies = list(mongo.db.movies.find({}, {"_id": 0}).sort(sort_by, sort_order))

    return render_template('home.html', movies=movies, sort_by=sort_by, order=order, is_logged_in=is_logged_in)


@app.route('/reminder')
def reminder_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    is_logged_in = True
    user_id = session['user_id']
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    movies = user.get('movies', [])

    return render_template('reminder.html', movies=movies, is_logged_in=is_logged_in)


# Ruta para ver cada pelicula
@app.route('/movies/name=<path:name>')
def movie_detail(name):
    is_logged_in = 'user_id' in session
    movie = mongo.db.movies.find_one({"Name": name})

    if movie is None:
        movie = mongo.db.movies.find_one({"Name": int(name)})

    if movie is None:
        abort(404)

    url, description = utilities.obtener_datos_pelicula(str(movie["Name"]), str(movie["Date"]))
    return render_template('movie.html', movie=movie, url=url, description=description, is_logged_in=is_logged_in)


# Ruta para añadir rating
@app.route('/submit_value', methods=['POST'])
def submit_value():
    input_value = request.form.get('input_value')
    movie_id = request.form.get('movie_id')

    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
    if movie:
        votes_str = movie.get("Votes", "0")
        rate_str = movie.get("Rate", "0")

        if votes_str == 'No Votes':
            votes = 0
        else:
            votes = int(str(votes_str).replace(',', ''))

        if rate_str == 'No Rate':
            rate = 0.0
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = mongo.db.users.find_one({"email": email})

        if user:
            user = mongo.db.users.find_one({"email": email, "password": password})
            if user:
                session.permanent = True # Inicar una nueva sesión
                session['user_id'] = str(user['_id'])
                return redirect(url_for("home"))
            else:
                return redirect(url_for("login"))
        else:
            new_user = mongo.db.users.insert_one({"email": email, "password": password, "movies": []})
            session.permanent = True # Inicar una nueva sesión
            session['user_id'] = str(new_user.inserted_id)
            return redirect(url_for("home"))

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)  # Cerrar la sesión del usuario
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)