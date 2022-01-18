import os
import json
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

# @app.route("/connect")
# def connect():
# 	target = request.form["target_user"]
# 	if r.checkUserExists(target):
# 		r.setConnection(username, target)
# 	else:
# 		flash("User does not exist")
# 	return redirect(request.referrer)

@app.route("/home")
def home():
	username = request.args.get("username")
	connect = r.getConnection(username)
	lastSong = r.getLastSong(username)
	return render_template("home.html", user=username, connection=connect, song=lastSong)

@app.route("/settings", methods=["GET", "POST"])
def settings():
	username = request.args.get("username", "")
	data = request.form
	if "current_pass" in data:
		pass_res = r.updatePassword(username, data["current_pass"], data["new_pass"])
		if pass_res == 1:
			flash("Successfully changed password!")
		else:
			flash(f"Something went wrong, error code: {pass_res}")
	elif "target" in data:
		connect_res = r.setConnection(username, data["target"])
		if connect_res == 1:
			flash("Successfully set connection!")
		else:
			flash(f"Something went wrong, error code: {connect_res}")
	else:
		app.logger.info(f"Username: {username}, Data: {data.keys()}")
	connect = r.getConnection(username)
	return render_template("settings.html", username=username, connection=connect)

@app.route("/share", methods=["GET", "POST"])
def share():
	username = request.args.get("username")
	song = request.form["song"]
	target = r.getConnection(username)
	if r.checkUserExists(target):
		msg = {
			"url": song,
			"name": "Am I Evil?",
			"artist": "Diamond Head",
			"artwork": "https://zrockr.com/user-files/uploads/2016/03/401_logo.png",
			"sender": username,
			"target": target
		}
		msgs = json.dumps(msg)
		target_data = r.getUserData(target)
		target_data["messages"].append(msgs)
		target_data["lastSong"] = msgs
		r.setUserData(target, target_data)
		return redirect(request.referrer)