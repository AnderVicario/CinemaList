from flask import Flask, jsonify, render_template, request, abort, url_for, redirect, session
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from bson.son import SON
from bson import ObjectId
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta
from datetime import datetime
import utilities
import os
import logging
import bcrypt


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = Flask(__name__)

# Configuración de la base de datos MongoDB
def read_mongo_password():
    file_path = '/run/secrets/mongodb_password'
    
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return os.environ.get('MONGODB_PASSWORD')

mongo_password = read_mongo_password()
app.secret_key = mongo_password
app.permanent_session_lifetime = timedelta(minutes=10)
app.config["MONGO_URI"] = f"mongodb://mongodb:{mongo_password}@mongodb:27017/movies?authSource=admin"
mongo = PyMongo(app)

# Configuración de Flask-Mail para usar Postfix como servidor SMTP
app.config.update(
    MAIL_SERVER='postfix',  # Docker service name
    MAIL_PORT=25,
    MAIL_USE_TLS=False,     # No TLS for internal postfix communication
    MAIL_USE_SSL=False,
    MAIL_DEFAULT_SENDER='noreply.cinemadocker@gmail.com'
)

mail = Mail(app)

# Ruta para enviar un correo
@app.route("/send_email")
def send_email():
    msg = Message("Hello", sender="noreply.cinemadocker@gmail.com", recipients=["andervicariozabala@gmail.com"])
    msg.body = "This is a test email."
    try:
        mail.send(msg)
        return "Email sent!"
    except Exception as e:
        return f"Error sending email: {str(e)}"

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


# Ruta para la lista de recordatorios
@app.route('/reminder')
def reminder_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    is_logged_in = True
    user_id = session['user_id']
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    user_movies_info = user.get('movies', [])

    movies = []
    for movie in user_movies_info:
        movie_data = mongo.db.movies.find_one({"_id": ObjectId(movie['movie'])})
        if movie_data:
            Name = movie_data.get('Name')
            Date = movie_data.get('Date')
            url, description = utilities.obtener_datos_pelicula(str(Name), str(Date))
            movies.append({
                "id": movie['movie'],
                "Name": Name,
                "Date": Date,
                "Picture": url,
                "Description": description,
                "ReminderDate": movie.get('date', 'Fecha no disponible')
            })

    return render_template('reminder.html', movies=movies, is_logged_in=is_logged_in)


# Ruta para actualizar recordatorios
@app.route('/update_reminder/<movie_id>', methods=['POST'])
def update_reminder(movie_id):
    new_date = request.form['reminder_date']
    user_id = session['user_id']

    # Actualizar fecha en la lista de películas del usuario
    mongo.db.users.update_one(
        {"_id": ObjectId(user_id), "movies.movie": ObjectId(movie_id)},
        {"$set": {"movies.$.date": new_date}}
    )

    return redirect(url_for('reminder_list'))


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


# Ruta para agregar/quitar película favorita
@app.route('/toggle_movie', methods=['POST'])
def toggle_movie():
    # Obtener la información del JSON enviado desde el cliente
    data = request.get_json()
    user_id = session.get('user_id')
    movie_id = data.get('movieId')
    
    if user_id and movie_id:
        # Buscar el usuario por el user_id
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        
        # Verifica si la película ya está en la lista
        if any(movie['movie'] == ObjectId(movie_id) for movie in user.get('movies', [])):
            # Eliminar la película si ya está en la lista
            mongo.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"movies": {"movie": ObjectId(movie_id)}}}
            )
            return jsonify({"status": "removed"})
        else:
            # Agregar la película si no está en la lista
            mongo.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"movies": {"movie": ObjectId(movie_id), "date": ""}}}
            )
            return jsonify({"status": "added"})

    return jsonify({"status": "error"}), 400


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


# Ruta para loguearte
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = mongo.db.users.find_one({"email": email})

        if user:
            # Verificar si la contraseña hasheada coincide
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                session.permanent = True
                session['user_id'] = str(user['_id'])
                return redirect(url_for("home"))
            else:
                # Contraseña incorrecta
                return redirect(url_for("login"))
        else:
            # Crear nuevo usuario con contraseña hasheada
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_user = mongo.db.users.insert_one({
                "email": email, 
                "password": hashed_password,
                "movies": []
            })
            session.permanent = True
            session['user_id'] = str(new_user.inserted_id)
            return redirect(url_for("home"))

    return render_template("login.html")


# Ruta para desloguearte
@app.route("/logout")
def logout():
    session.pop('user_id', None)  # Cerrar la sesión del usuario
    return redirect(url_for("login"))


# Enviar correos
def send_reminder_emails():
    with app.app_context():
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Buscar usuarios con películas asociadas a la fecha actual
        users_with_movies = mongo.db.users.find({
            "movies.date": today
        })
        
        for user in users_with_movies:
            email = user.get("email")
            id = user.get("_id")
            movies_today = []
            
            # Iterar sobre las películas y buscar sus títulos
            for movie_entry in user["movies"]:
                if movie_entry["date"] == today:
                    movie = mongo.db.movies.find_one({"_id": ObjectId(movie_entry["movie"])})
                    if movie:
                        movies_today.append(str(movie["Name"]))  # Agregar el título de la película a la lista
                        mongo.db.users.update_one(
                            {
                                "_id": ObjectId(id),
                                "movies": {
                                    "$elemMatch": {
                                        "movie": ObjectId(movie_entry["movie"]),
                                        "date": today
                                    }
                                }
                            },
                            {
                                "$set": {
                                    "movies.$.date": ""
                                }
                            }
                        )
                        logger.info(str(id) + "<--user, movie-->" + str(movie_entry["movie"]))
            
            if movies_today:  # Si hay películas programadas para hoy
                # Crear el cuerpo del mensaje con las películas
                movie_list = "\n".join(movies_today)
                msg_body = (
                    f"Hola!,\n\n"
                    f"Estas son las películas que tienes programadas para hoy:\n\n{movie_list}\n\n"
                    "¡Disfruta del cine!"
                )
                
                logger.info(msg_body)

                # Enviar el correo
                if email:
                    msg = Message(
                        "Recordatorio de películas", 
                        sender="noreply.cinemadocker@gmail.com", 
                        recipients=[email]
                    )
                    msg.body = msg_body
                    try:
                        mail.send(msg)
                        logger.info(f"Correo enviado a {email}")
                    except Exception as e:
                        logger.info(f"Error enviando correo a {email}: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminder_emails, 'interval', minutes=1)

def init_scheduler():
    if not scheduler.running:
        logger.info("Iniciando scheduler...")
        scheduler.start()
        logger.info("Scheduler iniciado correctamente")


if __name__ == '__main__':
    init_scheduler()
    app.run(host='0.0.0.0', port=5000)