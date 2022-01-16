import json
import os
from src.redis_client import RedisClient
from flask import (
	Flask, 
	render_template, 
	request, 
	redirect, 
	make_response, 
	url_for
)

app = Flask(__name__, template_folder="./templates")
r = RedisClient()

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/login/")
def login_screen():
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
				return home(username)
			else:
				print("Invalid password")
				return redirect(request.referrer)
		else:
			print("User doesn't exist")
			return redirect(request.referrer)
	elif target == "Register":
		if r.checkUserExists(username):
			return redirect(request.referrer)
		else:
			r.addUser(username)
			r.addUserData(username, password)
			return home(username)

@app.route("/home/")
def home(username=""):
	return render_template("home.html", name="")