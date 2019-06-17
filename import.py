import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create table books
db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR(20) NOT NULL, title TEXT NOT NULL, author VARCHAR(100) NOT NULL, year VARCHAR(20) NOT NULL)")
db.commit()

# Import data from csv file


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {
                   "isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()


if __name__ == "__main__":
    main()
