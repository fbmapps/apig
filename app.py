"""
TECHX BOT APPLICATION SERVER
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : MAY 2018
VERSION: 0.2
STATE: RC2
Main Application Server to run a Socket in port 5105.
This is the connecting point to invoke techxbot functionality
This in Python 3.6.5
micro framework is flask
"""

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2018 Cisco and/or its affiliates."
__license__ = "MIT"

# Libraries
# ========= Standard library ============
import os
import sys
import logging

# ========= Microframework ===========
# from flask import Flask
# ========== 3rd-Party ===============
from pyfiglet import Figlet
from halo import Halo

# ======== Custom Library =============
# from bot import techxbot
from apigw.apigw_server import app
import apigw.apigw_logger
# ============= Set Logger ================
logger = logging.getLogger("apigw.MAIN")


def splash_screen():
    """
    Create a Welcome Screen for the Script
    """
    figlet = Figlet(font="slant")
    banner = figlet.renderText("TechX API Gateway")
    print(banner)
    print("[+] 2020 TechX API Gateway www.cisco.com\n")


# Main Program
if __name__ == "__main__":
    splash_screen()
    spinner = Halo(spinner="dots")
    try:
        spinner.start(text="API Gateway is starting")
        spinner.succeed(text="API Gateway is running")
        port = int(os.environ.get("PORT", 5105))
        logger.info("API Gateway started Sucessfully!!")
        app.run(host='0.0.0.0', port=port, debug=True)
        logger.info("API Gateway Stopped")
    except Exception as err:
        spinner.fail(text="API Gateway fails")
        logger.error("Error Starting API Gateway : %s", err)
        sys.exit(1)
