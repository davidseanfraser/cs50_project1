@echo off
set FLASK_APP=application.py
set FLASK_DEBUG = 1
set DATABASE_URL=postgres://tfchcrecpltugr:bb46d293f43e7a367182c3d5012ababfd176bff2dbbf9d768781908cbf23a7d8@ec2-79-125-127-60.eu-west-1.compute.amazonaws.com:5432/dcr86ie0m016hb
flask run