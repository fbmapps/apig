"""
TECHX API GATEWAY (APIGW)
LOGGER FUNCTIONALITY
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
#import os
#import sys
import logging
import logging.handlers

# =========== Define a Logger ==============#
logger = logging.getLogger("apigw")
LOG_FILENAME = "apigw.log"

# set up the logger
logger.setLevel(logging.DEBUG)

# File Rotation
handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=2048000, backupCount=5
)

# File Logger
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Console Logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
