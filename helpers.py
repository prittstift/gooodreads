import requests

from flask import redirect, render_template, session
from functools import wraps


def prepare_bookpage(rows, rows_rev):

    goodreads_key = "qAwQTfh7LVqk7dcYK0wulg"

    class FoundBook:

        def __init__(self, rows, rows_rev, i):
            self.book_id = rows[i]["id"]
            self.isbn = rows[i]["isbn"]
            self.title = rows[i]["title"]
            self.author = rows[i]["author"]
            self.year = rows[i]["year"]
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                               params={"key": goodreads_key, "isbns": self.isbn})
            self.average_rating = res.json()["books"][0]["average_rating"]
            self.ratings_count = res.json()["books"][0]["work_ratings_count"]

            review_possible = True
            for j in range(len(rows_rev[i])):
                if rows_rev[i][j] != []:
                    if session["user_id"] == rows_rev[i][j]["user_id"]:
                        review_possible = False
            self.review_possible = review_possible

            usernames = []
            for j in range(len(rows_rev[i])):
                usernames.append(rows_rev[i][j]["username"])
            self.usernames = usernames

            ratings = []
            for j in range(len(rows_rev[i])):
                ratings.append(rows_rev[i][j]["rating"])
            self.ratings = ratings

            reviews = []
            for j in range(len(rows_rev[i])):
                reviews.append(rows_rev[i][j]["review"])
            self.reviews = reviews

            no_review = True
            if reviews != []:
                for review in reviews:
                    if review is not None:
                        no_review = False
            self.no_review = no_review

    results = []
    for i in range(len(rows)):
        results.append(FoundBook(rows, rows_rev, i))

    session["isbn"] = []
    for result in results:
        session["isbn"].append(result.isbn)

    session["book_id"] = []
    for result in results:
        session["book_id"].append(result.book_id)

    return render_template("book.html", results=results)


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
