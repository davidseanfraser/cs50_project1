@echo off
set FLASK_APP=application.py
set FLASK_DEBUG = 1
set DATABASE_URL=postgres://umbwtwbuirocfz:df30f8b0a30dbde81efa443582f80ec034f95355ea7d672f781e7c895788da9e@ec2-54-83-19-244.compute-1.amazonaws.com:5432/dcun8revm85ume
flask run