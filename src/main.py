import json
import os
from src.redis_client import RedisClient
from flask import (
	Flask, 
	render_template, 
	request, 
	redirect, 
	make_response, 
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
r = RedisClient()

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
		if r.checkUserExists(username):
			if r.checkPassword(username, password):
				return redirect(url_for("home", username=username))
			else:
				flash("Invalid password")
				return redirect(request.referrer)
		else:
			flash("User doesn't exist")
			return redirect(request.referrer)
	elif target == "Register":
		if r.checkUserExists(username):
			return redirect(request.referrer)
		else:
			r.addUser(username)
			r.addUserData(username, password)
			return redirect(url_for("home", username=username))

@app.route("/connect/<username>", methods=["GET", "POST"])
def connect(username=""):
	app.logger.info(f"Username: {username}")
	target = request.form["connect_target"]
	if r.checkUserExists(target):
		r.setConnection(username, target)
	else:
		flash("User does not exist")
	return redirect(request.referrer)

@app.route("/home/<username>")
def home(username=""):
	connect = r.getConnection(username)
	return render_template("home.html", user=username, connection=connect if connect else "Connect!")