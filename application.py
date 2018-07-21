import os
import configDev

from flask import Flask, session, render_template
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
    users = [{'username':'David', 'url':'haha'}, {'username':'Steph', 'url':'bunny'}]
    return render_template("index.html", users = users)

@app.route("/registration")
def registration():
    return render_template("registration.html", title='testing')
