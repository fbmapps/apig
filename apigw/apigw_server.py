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
import os
import logging
import hashlib
import hmac

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
    POST Calls Need To be signed by Webhook via PSK
    """
    payload = request.json
    logger.info("Webex Team resource : %s " , payload['resource'])

    # SIGNATURE with SECRET Key from Webhook
    raw_payload = request.data # This is required as raw, to match the signed Payload
    signed_payload = request.headers.get('X-Spark-Signature') #This Headers includes the Webhook Data Encode with the Secret Key
    if validate_webhook_secret(raw_payload, signed_payload):
        logger.info("SIGNED Webhook Callback received")
        the_response = apigw_webex_listener(payload)
    else:
        the_response = {"status_code" : 405, "status_info" : "Unsigned Request"}    

    return jsonify(the_response)


@app.route("/health", methods=["GET"])
def flask_webhook_health():
    """
    Return a I'm  ALive
    """
    iam_alive = {"status_code": 200, "status_info": "OK"}
    return jsonify(iam_alive)

# ==== General Usage Functions ====
def validate_webhook_secret(raw_payload, signed_payload):
    """
    Function to Validate POST from Webhook are valid with the secret Key
    input: Key
    Return True/False
    WEBEX BOT BEST PRACTICE
    /blog/building-a-more-secure-bot
    """
    skey = str(os.environ["WEBEX_WEBHOOK_SECRET_KEY"])
    bkey = bytes(skey, 'utf-8')
    hashed = hmac.new(bkey, raw_payload, hashlib.sha1)
    valid_payload = hashed.hexdigest()

    if valid_payload == signed_payload:
        valid_webhook = True
    else:
        valid_webhook = False

    return valid_webhook    
