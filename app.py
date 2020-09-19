import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

restricted = ["create", "edit", ""]

# from dotenv import load_dotenv
# dotenv_path = join(dirname(__file__), '.env')  # Path to .env file
# load_dotenv(dotenv_path)

# import smtplib, ssl

# port = 465  # For SSL

# Create a secure SSL context
# context = ssl.create_default_context()

# if not os.environ.get("EMAIL_PASS"):
#     raise RuntimeError("Email Password not set")

# with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#     server.login("pigcake999main@gmail.com", os.environ.get("EMAIL_PASS"))
#     # TODO: Send email here

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///speakup.db")

def apology(msg):
    return render_template("apology.html", message=msg)

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect("/dashboard")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        details = request.get_json(silent=True)

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":

            # Ensure email was submitted
            if not details['email']:
                return jsonify(error="Must provide an email"), 401

            # Ensure password was submitted
            elif not details['password']:
                return jsonify(error="Must provide password"), 401

            # Query database for email
            rows = db.execute("SELECT * FROM users WHERE email = :email", email=details['email'])

            # Ensure email exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["password"], details['password']):
                return jsonify(error="Invalid email and/or password"), 401

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            return jsonify(message="success"), 200

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auth/login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        details = request.get_json(silent=True)
        if not details["email"]:
            return jsonify(error="Must provide email"), 401

        elif not details["name"]:
            return jsonify(error="Must provide name"), 401

        # Ensure password was submitted
        elif not details["password"]:
            return jsonify(error="Must provide password"), 401

        elif not details["confirm-password"]:
            return jsonify(error="Sorry, passwords didn't match. Try Again!"), 401

        elif details["password"] != details["confirm-password"]:
            return jsonify(error="Sorry, passwords didn't match. Try Again!"), 401

        # Hash password
        hashed = generate_password_hash(details["password"])

        r = db.execute("INSERT INTO users (name, email, password) VALUES (:name, :email, :password)", name=details["name"], email=details['email'], password=hashed)

        if not r:
            return jsonify(error="email already being used"), 401

        session.clear()

        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=details["email"])

        session["user_id"] = rows[0]["id"]

        # db.execute("INSERT INTO verification (email) VALUES (:email)", email = details["email"])

        # message = """\
        # Subject: SpeakUp Email Verification

        # http://""" +

        return jsonify(message="success"), 200
    else:
        return render_template("auth/register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if session.get("user_id"):
        blogs = db.execute("SELECT * FROM blogs WHERE user_id = :user_id", user_id=session.get("user_id"))
        return render_template("dashboard.html", blogs=blogs, blogsLength=len(blogs))
    else:
        return redirect("/login")

@app.route("/blogs/create", methods=["GET", "POST"])
def blog():
        if request.method == "POST":
            availability = db.execute("SELECT * FROM blogs WHERE id=:id", id=request.form["name"])
            
            if len(availability) == 0 and request.form["name"] not in restricted:
                db.execute("INSERT INTO blogs (id, user_id, description, category) VALUES (:name, :user_id, :description, :category)", name=request.form["name"], user_id=session.get("user_id"), description=request.form["description"], category=request.form["category"])
                return redirect("/dashboard")
            else:
                return apology("That blog name is not available.")
        else: 
            if session.get("user_id"):
                categories = [
                    "Beauty",
                    "Business",
                    "Career",
                    "Cars",
                    "Celebrity Gossip",
                    "DIY",
                    "Design",
                    "Education",
                    "Engineering",
                    "Entertainment",
                    "Fashion",
                    "Films",
                    "Finance",
                    "Food",
                    "Gaming",
                    "Geography",
                    "Green",
                    "Health",
                    "History",
                    "Law",
                    "Lifestyle",
                    "Marketing",
                    "Money",
                    "Music",
                    "Nature",
                    "Parenting",
                    "Pet",
                    "Photography",
                    "Politics",
                    "Productive",
                    "Programming",
                    "Real Estate",
                    "SEO",
                    "Science",
                    "Shopping",
                    "Social Media",
                    "Sports",
                    "Technology",
                    "Travel",
                    "University",
                    "Wine"
                ]
                return render_template("createblog.html", categories=categories)
            else:
                return redirect("/login")

@app.route("/blogs/edit/<name>")
def edit(name):
    posts = db.execute("SELECT * FROM posts WHERE blog_id=:name", name=name)
    return render_template("editblog.html", name=name)

@app.route("/blogs/<name>/posts/create", methods=["GET", "POST"])
def createpost(name):
    if request.method == "GET":
        return render_template("createpost.html", name=name)
    else:
        posts = db.execute("SELECT * FROM posts WHERE blog_id=:name AND title=:title", name=name, title=request.form["title"])

        if len(posts) > 0 or request.form["title"] in restricted:
            return apology("You already have a post with that name.")
        else:
            post = request.form
            db.execute("INSERT INTO posts (title, description, blog_id) VALUES (:title, :blurb, :blog_id)", title=post["title"], blurb=post["blurb"], blog_id=name)

            getpost = db.execute("SELECT id FROM posts WHERE title=:title AND blog_id=:name", title=post["title"],  name=name)

            with open(os.getcwd() + "/posts/" + str(getpost[0]["id"]) + ".md", "w+") as f:
                f.write(post["markdown"])

            return redirect("/blogs/" + name + "/posts/" + post["title"])

@app.route("/blogs/<name>/posts/create", methods=["GET", "POST"])
def viewpost(name):
    if request.method == "GET":
        return render_template("createpost.html", name=name)
    else:
        posts = db.execute("SELECT * FROM posts WHERE blog_id=:name AND title=:title", name=name, title=request.form["title"])

        if len(posts) > 0:
            return apology("You already have a post with that name.")
        else:
            post = request.form
            db.execute("INSERT INTO posts (title, description, blog_id) VALUES (:title, :blurb, :blog_id)", title=post["title"], blurb=post["blurb"], blog_id=name)

            getpost = db.execute("SELECT id FROM posts WHERE title=:title AND blog_id=:name", title=post["title"],  name=name)

            with open(os.getcwd() + "/posts/" + str(getpost[0]["id"]) + ".md", "w+") as f:
                f.write(post["markdown"])

            return redirect("/blogs/" + name + "/posts/" + post["title"])

@app.route("/blogs/<name>")
def viewblog(name):
    blog = db.execute("SELECT * FROM blogs WHERE user_id=:user_id AND id=:name", user_id=session.get("user_id"), name=name)
    return render_template("blog/index.html", blog=blog[0])