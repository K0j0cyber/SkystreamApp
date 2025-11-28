from flask import Flask, render_template, request, redirect, session
import requests
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "replace_me_secure_key"
app.permanent_session_lifetime = timedelta(days=5)

# ============================
# DATABASE (Temporary Mock)
# ============================

users = {
    "admin": {"password": "admin123", "friends": [], "messages": []},
    "client": {"password": "client123", "friends": [], "messages": []}
}

posts = []

streams = [
    {"name": "SkyStream Live Channel", "status": "Live"},
    {"name": "Galaxy Gaming", "status": "Offline"},
    {"name": "Tech Today", "status": "Live"},
]

NEWS_URL = "https://newsdata.io/api/1/news?apikey=pub_12345&country=gh"


# ============================
# FUNCTIONS
# ============================

def get_news():
    try:
        r = requests.get(NEWS_URL)
        return r.json().get("results", [])[:6]
    except:
        return []


# ============================
# ROUTES
# ============================

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/login")

    news = get_news()
    return render_template("home.html",
                           user=session["user"],
                           posts=posts,
                           streams=streams,
                           news=news)


# ----------------------------
# ACCOUNT CREATION
# ----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            return render_template("register.html", error="Username already exists")

        # Create the user
        users[username] = {
            "password": password,
            "friends": [],
            "messages": []
        }

        return redirect("/login")

    return render_template("register.html")


# ----------------------------
# LOGIN
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check user
        if username in users and users[username]["password"] == password:
            session["user"] = username
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ----------------------------
# CREATE POST
# ----------------------------
@app.route("/post", methods=["POST"])
def create_post():
    if "user" not in session:
        return redirect("/login")

    content = request.form.get("content")
    if content:
        posts.append({"author": session["user"], "content": content})

    return redirect("/home")


# ----------------------------
# FRIEND SYSTEM
# ----------------------------
@app.route("/add_friend", methods=["POST"])
def add_friend():
    if "user" not in session:
        return redirect("/login")

    friend = request.form.get("friend")

    if friend in users:
        current_user = session["user"]
        if friend not in users[current_user]["friends"]:
            users[current_user]["friends"].append(friend)

    return redirect("/friends")


@app.route("/friends")
def friends():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]
    return render_template("friends.html",
                           friends=users[user]["friends"],
                           all_users=list(users.keys()))


# ----------------------------
# MESSAGING SYSTEM
# ----------------------------
@app.route("/messages", methods=["GET", "POST"])
def messages():
    if "user" not in session:
        return redirect("/login")

    current_user = session["user"]

    if request.method == "POST":
        receiver = request.form.get("receiver")
        message = request.form.get("message")

        if receiver in users and message:
            users[receiver]["messages"].append({
                "from": current_user,
                "message": message
            })

    return render_template("messages.html",
                           inbox=users[current_user]["messages"],
                           all_users=list(users.keys()))


# ----------------------------
# STREAMING PAGE (TikTok & Twitch Embeds)
# ----------------------------
@app.route("/streams")
def streams_page():
    if "user" not in session:
        return redirect("/login")

    return render_template("streams.html", streams=streams)


# ============================
# RUN APP
# ============================

if __name__ == "__main__":
    app.run(debug=True)
