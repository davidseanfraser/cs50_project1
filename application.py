import os
import configDev
import requests
import json

from flask import Flask, session, render_template, request, redirect, make_response, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


APIKEY = configDev.APIKEY
APISECRET = configDev.APISECRET

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/register", methods=["POST"])
def register():
    user = request.form.get("reg_username")
    password = hash(request.form.get("reg_password"))

    if db.execute("SELECT * FROM users WHERE username = :user", {"user": user}).rowcount == 0:
        db.execute("INSERT INTO users (username, password) VALUES (:user, :password)", {"user":user, "password": password})
        db.commit()

        resp = make_response(render_template("home.html", message="Welcome"))
        resp.set_cookie('userID', user)
        return resp
    return render_template("registration.html", message = "Username is already taken.  Try again.")

@app.route("/home", methods=["POST"])
def home():
    user = request.form.get("username")
    password = hash(request.form.get("password"))

    if db.execute("SELECT * FROM users WHERE username = :user AND password = :password", {"user":user, "password": password}).rowcount == 1:
        resp = make_response(render_template("home.html", message="Welcome"))
        resp.set_cookie('userID', user)
        return resp
        # render_template("home.html", message="Welcome")
    else:
        return render_template("index.html", message="Invalid Login - Try Again")

# @app.route("/home", methods = ["POST"])
# def home():
#     return render_template("home.html", message ="Welcome")

@app.route("/logout")
def logout():
    session["user_id"] = None
    return render_template("index.html", message="Goodbye")

@app.route("/search", methods= ["POST"])
def search():
    search_request = '%'+request.form.get("search_box")+'%'

    search_return = db.execute("SELECT * FROM books WHERE isbn LIKE :search OR title LIKE :search OR author LIKE :search LIMIT 10", {"search": search_request})

    if search_return.rowcount  == 0:
        return render_template("home.html", message="No results found")

    return render_template("search.html", search_arg = search_return)

@app.route("/search/<isbn>", methods= ["POST", "GET"])
def book_info(isbn):

    book = db.execute("SELECT * from books where isbn = :isbn", {'isbn': isbn}).fetchone()
    reviews = db.execute("SELECT * from reviews WHERE isbn = :isbn LIMIT 5", {'isbn': isbn})
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": APIKEY, "isbns": isbn}).json()
    goodread_reviews = res['books'][0]['reviews_count']
    goodread_avg_score = res['books'][0]['average_rating']
    return render_template("book_info.html", book=book, reviews = reviews, isbn = isbn, goodread_reviews=goodread_reviews, goodread_avg_score = goodread_avg_score)

@app.route("/submit_review", methods=["POST"])
def submit_review():
    score = request.form.get("optradio")
    comment = request.form.get("comment")
    user_id = request.cookies.get("userID")
    isbn = request.form.get("isbn_input")

    user_id = db.execute("SELECT user_id FROM users WHERE username = :user_id",{"user_id":user_id}).fetchone()
    user_id = user_id.user_id
    existing = db.execute("SELECT review_id FROM reviews WHERE isbn = :isbn AND user_id = :user_id", {"isbn": isbn, "user_id": user_id}).fetchone()



    if existing is not None:
        db.execute("DELETE FROM reviews WHERE review_id = :review_id", {"review_id": existing.review_id})
        db.commit()

    db.execute("INSERT INTO reviews (isbn, review, score, user_id) VALUES (:isbn, :comment, :score, :user_id)",{"isbn":isbn,"comment":comment, "score":score, "user_id":user_id})
    db.commit()

    return redirect(url_for('.book_info', isbn=isbn))

@app.route("/api/<isbn>")
def api_isbn(isbn):
    res = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    if res is None:
        return render_template("/404.html")

    reviews = db.execute("SELECT AVG(score) as avg, COUNT(score) as count FROM reviews WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    ret_dic = {'title': res.title, 'author': res.author, 'year': res.year,
    'isbn': isbn, 'review_count': reviews.count, 'average_score': reviews.avg}

    json_ret = json.dumps(ret_dic)

    return render_template("/api_isbn.html", json=json_ret)
