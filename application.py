import os
import requests

from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, prepare_bookpage

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


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def query(rows):

    rows_rev = []
    for i in range(len(rows)):
        rows_rev.append(db.execute("SELECT * FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id",
                                   {"book_id": rows[i]["id"]}).fetchall())

    return prepare_bookpage(rows, rows_rev)


@app.route("/",  methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@app.route("/api/<string:isbn>",  methods=["GET"])
@login_required
def isbn_api(isbn):

    # Make sure ISBN exists
    isbn_search = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    if isbn_search == []:
        return jsonify({"error": "Invalid isbn"}), 404

    # Get all data
    goodreads_key = "qAwQTfh7LVqk7dcYK0wulg"
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": goodreads_key, "isbns": isbn_search[0]["isbn"]})
    average_rating = res.json()["books"][0]["average_rating"]
    ratings_count = res.json()["books"][0]["work_ratings_count"]

    return jsonify({
        "title": isbn_search[0]["title"],
        "author": isbn_search[0]["author"],
        "year":  int(isbn_search[0]["year"]),
        "isbn":  isbn_search[0]["isbn"],
        "review_count":  ratings_count,
        "average_score":  float(average_rating)
    })


@app.route("/book",  methods=["GET", "POST"])
@login_required
def book():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if request.form.get("isbn"):

            # Query database for username
            rows = db.execute("SELECT * FROM books WHERE isbn LIKE CONCAT ('%', :isbn, '%')",
                              {"isbn": request.form.get("isbn")}).fetchall()

            return query(rows)

        # Ensure username was submitted
        elif request.form.get("title"):

            # Query database for username
            rows = db.execute("SELECT * FROM books WHERE title LIKE CONCAT ('%', :title, '%')",
                              {"title": request.form.get("title")}).fetchall()

            return query(rows)

        elif request.form.get("author"):

            # Query database for username
            rows = db.execute("SELECT * FROM books WHERE author LIKE CONCAT ('%', :author, '%')",
                              {"author": request.form.get("author")}).fetchall()

            return query(rows)

        else:
            if not request.form.get("rating") and not request.form.get("review"):
                return apology("must provide isbn, title or author", 400)

            else:

                # Query database for username
                book_id = session["book_id"][0]

                result = db.execute("INSERT INTO reviews (book_id, user_id, rating, review) VALUES (:book_id, :user_id, :rating, :review)", {
                                    "book_id": book_id, "user_id": session["user_id"], "rating": request.form.get("rating"), "review": request.form.get("review")})
                db.commit()
                if not result:
                    return apology("Something went wrong!", 400)

                rows = db.execute("SELECT * FROM books WHERE id = :book_id",
                                  {"book_id": book_id}).fetchall()

                return query(rows)

    else:
        return apology("must submit form via /search")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username;",
                          {"username": request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username!", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Missing password!", 400)

        # Ensure password was submitted second time
        elif not request.form.get("confirmation"):
            return apology("Confirm password!", 400)

        # Ensure password was correctly confirmed
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Confirm password!", 400)

        # Generate hash
        hash = generate_password_hash(request.form.get("password"))
        username = request.form.get("username")

        # db.execute failure?
        result = db.execute(
            "INSERT INTO users (username, hash) VALUES (:username, :hash)", {"username": username, "hash": hash})
        db.commit()
        if not result:
            return apology("Username already taken!", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchall()

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
