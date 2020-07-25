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

# ===== APIGW Libraries =======
# ==== Create a Logger ===
logger = logging.getLogger("apigw.COVID")

# ==== Class Blueprint ===
class CovidStats:
    """
    Simple Wrapper to COVID-19 Stats
    from https://api.covid19api.com
    """

    def __init__(self):
        logger.info("A New COVID Services Object created")
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
            logger.error("API Request failes : %s", err)
            resp = {}
        return resp

    def get_covid_summary(self, message):
        """
        Get Latest Info about Covid
        """
        logger.info("Action Request from bot for COVID Data : %s", message)
        endpoint = "/summary"
        data = self.query_api(endpoint)
        datapoint = str(data["Global"]["NewConfirmed"])
        reply = f"""
                 Here is the Latest COVID from Jhon Hopskin Data: \n
                 * **{datapoint}** new confirmed cases \n
                 * **{data["Global"]["TotalDeaths"]}** Deaths \n
                 * **{data["Global"]["TotalRecovered"]}** recovered \n
                 * **{data["Global"]["TotalConfirmed"]}** cases World-wide
                 """
        return reply
