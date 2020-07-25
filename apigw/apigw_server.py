"""
TECHX API GATEWAY
ALL APPLICATION SERVER
URIS FOR WEBHOOKS CALL BACKS ARE DEFINED HERE
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
"""

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"

# Libraries
# ========= Standard library ============
# import os
# import sys
import logging

# ========= Microframework ===========
from flask import Flask, jsonify, request

# ==== Custom Libraries ===========
# import apigw.apigwlogger
from apigw.apigw_webex import apigw_webex_listener

# ==== Flask Instance =============
app = Flask(__name__)

# ==== Set a Logger =====
logger = logging.getLogger("apigw.FLASK_SERVER")
# ====== Flask URI =====
@app.route("/")
def homepage():
    """
    Set a Home Page URI
    """
    logger.info("Incoming Request to /")
    body = """
    <h1> API Gateway  WebServer !!! </h1>
    """
    logger.info("Request Served")
    return body


@app.route("/", methods=["POST"])
def flask_webex_bot():
    """
    Entry Point for Message from Webex Team CallBack
    """
    payload = request.json
    logger.info("Webex Team resource : %s " , payload['resource'])
    the_response = apigw_webex_listener(payload)

    return jsonify(the_response)


@app.route("/health", methods=["GET"])
def flask_webhook_health():
    """
    Return a I'm  ALive
    """
    iam_alive = {"status_code": 200, "status_info": "OK"}
    return jsonify(iam_alive)
