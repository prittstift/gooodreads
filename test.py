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

rows = db.execute("SELECT * FROM books WHERE title LIKE CONCAT ('%', :title, '%')",
                  {"title": "Lady"}).fetchall()

rows_rev = []
for i in range(len(rows)):
    rows_rev.append(db.execute("SELECT * FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id",
                               {"book_id": rows[i]["id"]}).fetchall())

usernames = db.execute(
    "SELECT username FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id", {"book_id": 11}).fetchall()

user_ids = []
for i in range(len(rows)):
    user_ids.append(db.execute(
        "SELECT user_id FROM reviews WHERE book_id = :book_id", {"book_id": rows[i]["id"]}).fetchall())

print(rows)
print(rows_rev[1][0]["username"])
