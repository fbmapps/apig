"""
TECHX API GATEWAY
ALL APPLICATION SERVER
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
from flask import Flask, jsonify
# ==== Custom Libraries ===========
# import apigw.apigwlogger
# ==== Flask Instance =============
app = Flask(__name__)

#==== Set a Logger =====
logger = logging.getLogger('apigw.FLASK_SERVER')
# ====== Flask URI =====
@app.route("/")
def homepage():
    """
    Set a Home Page URI
    """
    logger.info('Incoming Request to /')
    body = """
    <h1> API Gateway  WebServer !!! </h1>
    """
    logger.info('Request Served')
    return body
