"""
TECHX API GATEWAY
GENERIC API CALLS TO EXTERNAL SERVICES
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

# ==== Create a Logger ===
logger = logging.getLogger('apigw.GENERIC')

# ==== Class Blueprint ===
class CovidStats:
    """
    Simple Wrapper to COVID-19 Stats
    from https://api.covid19api.com
    """

    def __init__(self):
        self.api_url = "https://api.covid19api.com"

    def query_api(self, enpoint):
        """
        Helper for API Call
        """
        url = self.api_url + enpoint
        try:
            rx_answer = requests.get(url, verify=False)
            resp = json.loads(rx_answer.text)
        except requests.exceptions.RequestException as err:
            logger.error('API Request failes : %s', err)
            resp = {}
        return resp

    def get_covid_summary(self):
        """
        Get Latest Info about Covid
        """
        endpoint = "/summary"
        data = self.query_api(endpoint)
        return data
