"""
TECHX API GATEWAY
API GATEWAY FOR MERAKI
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
"""

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"

# === import libraries ====
import os
import json
import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# === Disable SSL Warnings ===
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# === Define a Logger ========
logger = logging.getLogger("apigw.MerakiWorker")
# === Class Blueprint
class APIGWMerakiWorker:
    """
    Object to wrap up all the Meraki Calls
    Requires
    MERAKI_API_TOKEN
    MERAKI_ORG
    """

    def __init__(self, meraki_org="", meraki_net=""):
        self.__name__ = "APIGW MERAKI Worker"
        if meraki_org in [""]:
            # if no meraki ORG or NET use Default Meraki Org and Net
            self.meraki_org = str(os.environ["MERAKI_ORG"])
        elif meraki_net in [""]:
            self.meraki_net = str(os.environ["MERAKI_DEFAULT_NETWORK"])
        else:
            self.meraki_org = meraki_org
            self.meraki_net = meraki_net

    def show_meraki_network(self, job_req):
        """
        GET Meraki Netwok ID
        params
        return:
        Network ID String
        """
        logger.info("Job Received: %s", job_req)
        api_uri = f"/v1/organizations/{self.meraki_org}/networks"
        data = get_meraki_api_data(api_uri)
        net_json = {}
        # Select the Mmeraki Network
        for network in data:
            net_info = network
            
         
        message = f"You are connecting to **{net_info['name']}**, which have this type of products \n"
        for product in net_info["productTypes"]:
            message += f"* **{product}**  \n"
    
        #message = net_json
        return message

    def get_meraki_devices(self, job_req):
        """
        Get Devices attached to Meraki Network
        job_req: Message from Dispatcher
        """
        logger.info("Job Received : %s", job_req)
        api_uri = f"/v1/networks/{self.meraki_net}/devices"
        data = get_meraki_api_data(api_uri)
        # Prepare Message
        return data


# === Meraki API CRUD Operations =====
## === Common Paramenters
api_headers = {}
api_headers["X-Cisco-Meraki-API-Key"] = str(os.environ["MERAKI_API_KEY"])
api_headers["Content-Type"] = "application/json"
API_URL = "https://api.meraki.com/api"
## === Functions
def get_meraki_api_data(api_uri):
    """
    Common Function to send GET Request to Meraki API
    param:
    api_uri = resource endpoint
    api_header = special header with api_key
    return:
    JSON data
    """
    url = API_URL + api_uri
    a_response = requests.get(url, headers=api_headers, verify=False)
    if a_response.status_code == 200:
        data = json.loads(a_response.text)
        logger.info("Meraki GET operation suceeded : %s ", api_uri)
    else:
        data = {}
        logger.info("Meraki GET Operation failed : %s", a_response.status_code)
    return data


def decode_meraki_model(model):
    """
    Receive Model ID
    Return a Huma Readable Label
    """
    model_label = ""

    if "MX" in model:
        model_label = "appliance"
    if "MS" in model:
        model_label = "switch"
    if "MR" in model:
        model_label = "wireless"
    if "MV" in model:
        model_label = "camera"
    if "MC" in model:
        model_label = "phone"

    return model_label


def meraki_api_enable():
    """
    Validate If Meraki Token is Set
    Return True/False
    """

    token = str(os.environ["MERAKI_API_KEY"])
    if token in [""]:
        return False
    else:
        return True
