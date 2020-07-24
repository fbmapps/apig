#!/bin/bash

# Start GUNICORN server for Flask App
# syntaxis gunicorn -b (BIND) <SERVER-ADDRESS>:<PORT> <main file>:<flask app>

gunicorn -b 0.0.0.0:5105 app:app
