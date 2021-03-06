import os
import json
from src.url_parser import URLParser
from src.postgres_controller import PostgresController
from src.redis_client import RedisClient
from flask import (
	Flask, 
	render_template, 
	request, 
	redirect,
	url_for,
	flash,
	get_flashed_messages
)

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__, template_folder="./templates")
app.secret_key = os.environ.get("SECRET_KEY")
p = PostgresController()

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/login/")
def login():
	return render_template("login.html")

@app.route("/auth/", methods=["GET", "POST"])
def auth():
	data = request.form # all data goes by name attribute
	username = data["username"]
	password = data["password"]
	target = data["login"]

	if target == "Login":
		if p.checkUserExists(username):
			if p.checkPassword(username, password):
				return redirect(url_for("home", username=username))
			else:
				flash("Invalid password")
				return redirect(request.referrer)
		else:
			flash("User doesn't exist")
			return redirect(request.referrer)
	elif target == "Register":
		if p.checkUserExists(username):
			return redirect(request.referrer)
		else:
			p.insertUser(username, password)
			return redirect(url_for("home", username=username))

@app.route("/home")
def home():
	username = request.args.get("username")
	connect = p.getConnection(username)
	lastSong = p.getLastSong(username)
	if not lastSong:
		lastSong = {}
	else:
		lastSong = json.loads(lastSong)
	return render_template("home.html", user=username, connection=connect, song=lastSong)

@app.route("/settings", methods=["GET", "POST"])
def settings():
	username = request.args.get("username", "")
	data = request.form
	app.logger.info(data.keys())
	if "current_pass" in data:
		if p.updatePassword(username, data["current_pass"], data["new_pass"]):
			flash("Successfully changed password!")
		else:
			flash(f"Something went wrong when changing password")
	elif "unset_connection" in data:
		if p.updateConnection(username, "*"):
			flash("Successfully unset connection!")
	elif "target" in data:
		if p.getConnection(data["target"]):
			flash("User already has a connection! Ask them to unset first.")
		else:
			if p.updateConnection(username, data["target"]):
				flash("Successfully set connection!")
			else:
				flash("User doesn't exist for connecting!")
	else:
		app.logger.info(f"Username: {username}, Data: {data.keys()}")
	connect = p.getConnection(username)
	return render_template("settings.html", username=username, connection=connect)

@app.route("/share", methods=["GET", "POST"])
def share():
	username = request.args.get("username", "")
	song = request.form["song"]
	target = p.getConnection(username)
	if target:
		parser = URLParser(song)
		song_obj = parser.process()
		app.logger.info(f"Song_obj: {song_obj}")
		if song_obj:
			song_obj["sender"] = username
			song_obj["target"] = target
			song_obj_string = json.dumps(song_obj)
			p.updateSongs(target, song_obj_string)
			p.updateLastSong(target, song_obj_string)
		else:
			flash("Error sharing!")
	else:
		flash("You don't have a connection yet!")
	return redirect(request.referrer)

@app.route("/songs")
def songs():
	username = request.args.get("username")
	connection = request.args.get("connection")
	song_list = p.getSongs(username)
	song_list = [json.loads(song) for song in song_list]
	return render_template("songs.html", username=username, connection=connection, songs=song_list)

