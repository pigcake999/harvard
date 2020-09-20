import os, random, string, markdown2
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from mailjet_rest import Client

restricted = ["create", "edit", ""]

api_key = '4f3c956860456e687b6c181e48aaedab'
api_secret = '5ac9350dac389b2b7d73832ad4038ed0'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

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
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///speakup.db")

def apology(msg):
    return render_template("apology.html", message=msg)
def message(msg):
    return render_template("message.html", message=msg)

@app.route("/")
def index():
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

        rows = db.execute("SELECT * FROM users WHERE email = :email", email=details["email"])

        if len(rows) > 0:
            return jsonify(error="Someone is already using that email!"), 401

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
            availability = db.execute("SELECT * FROM blogs WHERE id=:id", id=request.form["name"].lower())
            
            if len(availability) == 0 and request.form["name"] not in restricted:
                db.execute("INSERT INTO blogs (id, user_id, description, category) VALUES (:name, :user_id, :description, :category)", name=request.form["name"].lower(), user_id=session.get("user_id"), description=request.form["description"], category=request.form["category"])
                return redirect("/dashboard")
            else:
                return apology("That blog name is not available.<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")
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
    blog = db.execute("SELECT user_id FROM blogs WHERE id=:id", id=name)
    if session.get("user_id"):
        if str(session.get("user_id")) == str(blog[0]["user_id"]):
            posts = db.execute("SELECT * FROM posts WHERE blog_id=:name", name=name.lower())
            return render_template("editblog.html", posts=posts, name=name.lower())
        else:
            return apology("You don't own that blog!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")

@app.route("/blogs/<name>/posts/create", methods=["GET", "POST"])
def createpost(name):
    blog = db.execute("SELECT user_id FROM blogs WHERE id=:id", id=name)
    if session.get("user_id"):
        if str(session.get("user_id")) == str(blog[0]["user_id"]):
            if request.method == "GET":
                return render_template("createpost.html", name=name.lower())
            else:
                posts = db.execute("SELECT * FROM posts WHERE blog_id=:name AND link=:link", name=name.lower(), link=request.form["link"].lower())

                if len(posts) > 0 or request.form["link"] in restricted:
                    return apology("You already have a post with that name.<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")
                else:
                    post = request.form
                    db.execute("INSERT INTO posts (link, title, description, blog_id) VALUES (:link, :title, :blurb, :blog_id)", link=post["link"].lower(), title=post["title"], blurb=post["blurb"], blog_id=name)

                    getpost = db.execute("SELECT id FROM posts WHERE link=:link AND blog_id=:name", link=post["link"].lower(),  name=name)

                    with open(os.getcwd() + "/posts/" + str(getpost[0]["id"]) + ".md", "w+") as f:
                        f.write(post["markdown"])

                    return redirect("/blogs/" + name + "/posts/" + post["link"])
        else:
            return apology("You don't own that blog!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")

@app.route("/blogs/<name>")
def viewblog(name):
    blog = db.execute("SELECT * FROM blogs WHERE id=:name", name=name.lower())
    posts = db.execute("SELECT * FROM posts WHERE blog_id=:name", name=name.lower())
    user = db.execute("SELECT * FROM users WHERE id=:id", id=int(blog[0]["user_id"]))
    owned = False
    if session.get("user_id"):
        if str(blog[0]["user_id"]) == str(user[0]["id"]):
            owned = True
    return render_template("blog/index.html", blog=blog[0], posts=posts, author=user[0]["name"], owned=owned)

@app.route("/blogs/<name>/posts/<postname>")
def viewpost(name, postname):
    blog = db.execute("SELECT * FROM blogs WHERE id=:name", name=name.lower())
    posts = db.execute("SELECT * FROM posts WHERE blog_id=:name AND link=:link", name=name.lower(), link=postname.lower())
    user = db.execute("SELECT * FROM users WHERE id=:id", id=int(blog[0]["user_id"]))
    with open(os.getcwd() + "/posts/" + str(posts[0]["id"]) + ".md", "r") as f:
        content = f.read()
        content = markdown2.markdown(content)
        owned = False
        if session.get("user_id"):
            if str(blog[0]["user_id"]) == str(user[0]["id"]):
                owned = True
        return render_template("blog/post.html", blog=blog[0], post=posts[0], author=user[0]["name"], markdown=content, owned=owned)

@app.route("/delete/<name>/<postname>")
def deletepost(name, postname):
    blog = db.execute("SELECT user_id FROM blogs WHERE id=:id", id=name)
    if str(session.get("user_id")) == str(blog[0]["user_id"]):
        db.execute("DELETE FROM posts WHERE link=:link", link=postname)
        return message("Post deleted!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")
    else:
        return apology("You don't own that blog!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")

@app.route("/delete/<name>")
def deleteblog(name):
    blog = db.execute("SELECT user_id FROM blogs WHERE id=:id", id=name)
    if str(session.get("user_id")) == str(blog[0]["user_id"]):
        db.execute("DELETE FROM blogs WHERE id=:id", id=name)
        return message("Blog deleted!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")
    else:
        return apology("You don't own that blog!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template("auth/forgotpassword.html")
    else:
        users = db.execute("SELECT * FROM users WHERE email=:email", email=request.form["email"])
        if len(users) > 0:
            check = db.execute("SELECT id FROM forgot WHERE email=:email", email=request.form["email"])
            
            if len(check) > 0:
                return apology("That account has already requested a password reset.<br><a class='btn btn-primary' href='/login'>Return to login</a>")
            else:
                getid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                db.execute("INSERT INTO forgot (id, email) VALUES (:id, :email)", id=getid, email=request.form["email"])

                data = {
                    'Messages': [
                        {
                            "From": {
                                "Email": "999pigcake@gmail.com",
                                "Name": "SpeakUp"
                            },
                            "To": [
                                {
                                "Email": request.form["email"]
                                }
                            ],
                            "Subject": "Reset your password.",
                            "HTMLPart": "<h3>Reset your password</h3><a href='http://cbrfinalproject.herokuapp.com/reset/"+str(getid)+"'>http://localhost:5000/reset/"+str(getid)+"</a>",
                            }
                    ]
                }
                result = mailjet.send.create(data=data)
                print(result.status_code)
                print(result.json())

                return message("Check your email for a password reset link.<br><a class='btn btn-primary' href='/login'>Return to login</a>")
        else:
            return apology("There is no account with that email.<br><a class='btn btn-primary' href='/login'>Return to login</a>")

@app.route("/reset/<id>", methods=["GET", "POST"])
def reset(id):
    if request.method == "GET":
        ids = db.execute("SELECT * FROM forgot WHERE id=:id", id=id)
        
        if len(ids) > 0:
            return render_template("auth/reset.html")
        else:
            return redirect("/login")
    else:
        if request.form["password"] == request.form["confirm"]:
            hashed = generate_password_hash(request.form["password"])
            getemail = db.execute("SELECT email FROM forgot WHERE id=:id", id=id)
            getemail = getemail[0]["email"]

            db.execute("UPDATE users SET password=:hashed WHERE email=:email", hashed=hashed, email=getemail)

            db.execute("DELETE FROM forgot WHERE email=:email", email=getemail)

            return message("Passwords changed.<br><a class='btn btn-primary' href='/login'>Return to login</a>")
        else:
            return apology("Passwords didn't match.<br><a class='btn btn-primary' href='/login'>Return to login</a>")

@app.route("/blogs")
def weirdlink():
    return redirect("/dashboard")

@app.route("/blogs/<name>/posts/<postname>/edit", methods=["GET", "POST"])
def editpost(name, postname):
    blog = db.execute("SELECT user_id FROM blogs WHERE id=:id", id=name)
    if session.get("user_id"):
        if str(session.get("user_id")) == str(blog[0]["user_id"]):
            if request.method == "GET":
                info = db.execute("SELECT * FROM posts WHERE blog_id=:name AND link=:link", name=name, link=postname)
                if len(info) > 0:
                    with open(os.getcwd() + "/posts/" + str(info[0]["id"]) + ".md", "r") as f:
                        content = f.read()
                        return render_template("editpost.html", name=name.lower(), info=info[0], content=content)
                else:
                    return apology("That post doesn't exist or you don't own that blog!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")
            else:
                posts = db.execute("SELECT * FROM posts WHERE blog_id=:name AND link=:link", name=name.lower(), link=postname)

                if len(posts) < 1:
                    return apology("That post no longer exists.<br><a class='btn btn-primary' href='/blogs/"+name+"'>Return to blog</a>")
                else:
                    post = request.form
                    db.execute("UPDATE posts SET link=:link, title=:title, description=:blurb, blog_id=:blog_id WHERE link=:oldlink", link=post["link"].lower(), title=post["title"], blurb=post["blurb"], blog_id=name, oldlink=postname)

                    getpost = db.execute("SELECT id FROM posts WHERE link=:link AND blog_id=:name", link=post["link"].lower(),  name=name)

                    with open(os.getcwd() + "/posts/" + str(getpost[0]["id"]) + ".md", "w+") as f:
                        f.write(post["markdown"])

                    return redirect("/blogs/" + name + "/posts/" + post["link"])
        else:
            return apology("You don't own that blog!<br><a class='btn btn-primary' href='/dashboard'>Return to dashboard</a>")