import requests

from flask import redirect, render_template, session
from functools import wraps


def prepare_bookpage(rows, usernames, user_ids, review_possible):
    book_id = rows[0]["id"]
    isbn = rows[0]["isbn"]
    title = rows[0]["title"]
    author = rows[0]["author"]
    year = rows[0]["year"]
    ratings = []
    for i in range(len(rows)):
        ratings.append(rows[i]["rating"])
    reviews = []
    for i in range(len(rows)):
        reviews.append(rows[i]["review"])

    no_review = True
    if reviews != []:
        for review in reviews:
            if review is not None:
                no_review = False

    session["isbn"] = []
    session["isbn"].append(isbn)

    session["book_id"] = []
    session["book_id"].append(book_id)

    goodreads_key = "qAwQTfh7LVqk7dcYK0wulg"
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": goodreads_key, "isbns": isbn})

    average_rating = res.json()["books"][0]["average_rating"]
    ratings_count = res.json()["books"][0]["work_ratings_count"]
    return render_template("book.html", isbn=isbn, title=title, author=author, year=year, ratings=ratings, reviews=reviews, average_rating=average_rating, ratings_count=ratings_count, usernames=usernames, review_possible=review_possible, no_review=no_review)


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
