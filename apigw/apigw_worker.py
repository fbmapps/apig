"""
TECHX API GATEWAY
GENRIC WORKER CLASS TO API CALLS TO EXTERNAL SERVICES
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
"""
__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"

# ====== Libraries =========
import json
import logging
import requests

# ===== APIGW Libraries =======
# ==== Create a Logger ===
logger = logging.getLogger("apigw.APIGWorker")

# ==== Class Blueprint ===
class APIGWorker:
    """
    Base Worker for API Calls operation
    """
    def __init__(self, api_url):
        self.__name__ = "APIGW Worker"
        self.api_url = api_url
        logger.info("APIGW Ready : %s", self.__name__)

    def query_api(self, api_endpoint, api_headers):
        """
        APIGW Worker API Caller
        params:
        api_enpoint = The URI call like /v1/dasdasd
        api_method = GET,POST,PUT,PATCH,DELETE
        api_headers = Any custom header
        return:
        a JSON Response
        """
        url = self.api_url + api_endpoint
        headers = api_headers
        try:
            rx_answer = requests.get(url, headers=headers, verify=False)
            resp = json.loads(rx_answer.text)
            logger.info("APIGW Worker request completed sucessfully")
        except requests.exceptions.RequestException as err:
            logger.error("APIGW Worker request failed : %s", err)
            resp = {}
        return resp
