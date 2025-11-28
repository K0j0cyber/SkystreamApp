from flask import Flask, render_template, request, redirect, session
import requests
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "replace_me_secure_key"
app.permanent_session_lifetime = timedelta(days=5)

# Mock database
users = {
    "admin": "admin123",
    "client": "client123"
}

posts = []
streams = [
    {"name": "SkyStream Live Channel", "status": "Live"},
    {"name": "Galaxy Gaming", "status": "Offline"},
    {"name": "Tech Today", "status": "Live"},
]

NEWS_URL = "https://newsdata.io/api/1/news?apikey=pub_12345&country=gh"


def get_news():
    try:
        r = requests.get(NEWS_URL)
        return r.json().get("results", [])[:6]
    except:
        return []


@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/home")
def home():
    news = get_news()
    return render_template("home.html", posts=posts, streams=streams, news=news)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["user"] = username
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/post", methods=["POST"])
def create_post():
    if "user" not in session:
        return redirect("/login")

    content = request.form.get("content")
    if content:
        posts.append({"author": session["user"], "content": content})

    return redirect("/home")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets the PORT automatically
    app.run(host="0.0.0.0", port=port, debug=True)
