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
    def __init__(self, requestor_name, meraki_org="", meraki_net=""):
        self.__name__ = "APIGW MERAKI Worker"
        self.job_owner = requestor_name
        if meraki_org in [""]:
            # if no meraki ORG or NET use Default Meraki Org and Net
            self.meraki_org = str(os.environ["MERAKI_ORG"])
        else:
            self.meraki_org = meraki_org

        if meraki_net in [""]:
            self.meraki_net = str(os.environ["MERAKI_DEFAULT_NETWORK"])
        else:
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
        # Select the Mmeraki Network
        for network in data:
            net_info = network

        message = f"You are connecting to **{net_info['name']}**, which have this type of products \n"
        for product in net_info["productTypes"]:
            message += f"* **{product}**  \n"

        # message = net_json
        return message

    def show_meraki_vlans(self, job_req):
        """
        Show All Vlans Associated to Meraki Network
        job_req: Message from Dispatcher
        return a message
        """
        logger.info("Job Received : %s", job_req)
        api_uri = f"/v1/networks/{self.meraki_net}/appliance/vlans"
        data = get_meraki_api_data(api_uri)
        # Parse the JSON
        message = f"There are {len(data)} vlans in the Network. Details:  \n"
        for vlan in data:
            message += f"* **{vlan['name']}** |  ID: **{vlan['id']}** | Subnet: **{vlan['subnet']}**  \n"

        return message

    def show_meraki_switch(self, job_req):
        """
        Show All Switches Associated to Meraki Network
        job_req: Message from Dispatcher, parse the request
        device_type = mx, ms, mv, mr, mc, wireless, switch, appliance
        return a message
        """
        logger.info("Job Received : %s", job_req)
        api_uri = f"/v1/networks/{self.meraki_net}/devices"
        data = get_meraki_api_data(api_uri)
        # Parse the JSON
        message = "Here is the detail:  \n"
        device_counter = 0
        for device in data:
            device_type = decode_meraki_model(device["model"])
            if "switch" in device_type:
                message += f"* **{device['name']}** |  IP: **{device['lanIp']}** | Serial: **{device['serial']}**  \n"
                device_counter += 1
        message += f"Total: **{device_counter}**  \n"        
        return message

    def change_port_vlan(self, job_req):
        """
        Change a Switch Port and assign a vlan
        params:
        job_req: Message from Dispatcher
        return: Job Action Message
        API V1
        """
        #Extract parameters from job_req
        #job_params
        #job_params[0]: Bot Command
        #job_params[1]: Switch IP Address
        #job_params[2]: Port Number
        #job_params[3]: Vlan ID
        devicon = chr(0x2757) + chr(0xFE0F)
        job_params = job_req.split()
        if len(job_params) < 4:
            #Not Enough info provided
            message = f" Job Request is incomplete, please provide Switch IP, Switch-Port, Vlan-ID ie _change-port-vlan 1.1.1.1 10 101 \n"
        else:
            #STEP 0: Initialize all the parameters
            ip_addr = job_params[1]
            port_id = job_params[2]
            vlan_id = job_params[3]
            #STEP 1: Validations
            #STEP 1-1: GET Switch Serial Number
            serial_id = get_switch_serial(ip_addr, self.meraki_net)
            if serial_id in [""]:
                message = f"{devicon} **There is not switch with that IP**"
                logger.error("VALIDATION failed Switch serial not Found %s", ip_addr)
                return message
            else:
                logger.info("VALIDATION Succeeded Switch serial Found %s", serial_id)

            #STEP 1-2: Validate Vlans ID
            vlan_exists, vlan_name = validate_vlan(vlan_id, self.meraki_net)
            if vlan_exists:
                logger.info("VALIDATION Succeeded Vlan ID Valid for %s Name: %s", vlan_id, vlan_name)
            else:
                logger.error("VALIDATION failed Vlan ID not Found %s", vlan_id)
                message = f"{devicon} **Invalid VLAN ID**"
                return message

            #STEP 1-3: Validate Port ID
            if validate_port(port_id, serial_id):
                logger.info("VALIDATION Succeeded Port ID Valid %s", port_id)
            else:
                logger.error("VALIDATION failed Port ID not Found %s", port_id)
                message = f"{devicon} **Invalid Port ID**"
                return message

            #STEP 2: Prepare the Payload
            port_payload = {}
            port_payload["name"] = f"Port changed by {self.job_owner} to {vlan_name.upper()} via Teams"
            port_payload["tags"] = ["Changed","Automation", "WebexBot", "DevOps"]
            port_payload["vlan"] = vlan_id
            port_payload["type"] = "access"
            logger.info("JSON Data to Port Update %s ", json.dumps(port_payload))

            #STEP 3: Send The Change to API
            api_uri = f"/v1/devices/{serial_id}/switch/ports/{int(port_id)}"
            data = update_via_meraki_api(api_uri, port_payload)
            if data:
                logger.info("Port updated successfully job_owner %s : ", self.job_owner)
                message = "**Port Update has been applied Sucesfully**  \n"
                message += F"* Job Owner: **{self.job_owner}**  \n"
                message += f"* PortID **{data['portId']}**  \n"
                message += f"* Port Name **{data['name']}**  \n"
                message += f"* Port Type **{data['type']}**  \n"
                message += f"* VLAN ID **{data['vlan']}**  \n"
                message += f"* Voice Vlan **{data['voiceVlan']}**  \n"
            else:                
                logger.error("Port update failed : ") 
                message = f"{devicon} Port Update incomplete"
        return message        


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

def update_via_meraki_api(api_uri, payload):
    """
    PUT Task sended to Meraki
    api_uri = resource endpoint
    api_header = special header with api_key
    payload = Data to Update, conforming API format 
    """
    url = API_URL + api_uri
    update_data = json.dumps(payload)
    make_update = requests.put(url, headers=api_headers, data=update_data, verify=False)
    if make_update.status_code == 200:
        data = json.loads(make_update.text)
        logger.info("Meraki PUT operation suceeded : %s ", api_uri)
    else:
        data = {}
        logger.info("Meraki PUT Operation failed : %s", make_update.status_code)
    return data

# === Meraki Helpers Functions
def decode_meraki_model(model):
    """
    Receive Model ID
    Return a Human Readable Label
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

def get_switch_serial(ip_addr, meraki_net):
    """
    Helper to Retrieve Switch Serial from IP
    params: IP Address, Meraki Network
    return: Serial
    """
    serial_id = ""
    api_uri = f"/v1/networks/{meraki_net}/devices"
    data = get_meraki_api_data(api_uri)
    for device in data:
        device_type = decode_meraki_model(device["model"])
        if "switch" in device_type: 
            if ip_addr in device["lanIp"]:
                serial_id = str(device["serial"]).strip()
                logger.info("Switch Found! Serial %s" , serial_id)            
    return serial_id

def validate_vlan(vlan_id, meraki_net):
    """
    Helper to Validate if a Vlan ID exist
    params: Vlan ID, Meraki Network ID
    returns: True/False
    API V0
    """
    check_vlan = False
    vlan_name = ""
    api_uri = f"/v0/networks/{meraki_net}/vlans/{vlan_id}"
    data = get_meraki_api_data(api_uri)
    if data:
        check_vlan = True
        vlan_name = data["name"].strip()
    else:
        check_vlan = False
    return check_vlan, vlan_name

def validate_port(port_id, serial_id):
    """
    Helper to Validate if a Vlan ID exist
    params: Vlan ID, Meraki Network ID
    returns: True/False
    API V1
    """
    check_port = False
    api_uri = f"/v1/devices/{serial_id}/switch/ports/{port_id}"
    data = get_meraki_api_data(api_uri)
    if data:
        check_port = True
    else:
        check_port = False
    return check_port


def meraki_api_enable():
    """
    Validate If Meraki Token is Set
    Return True/False
    """

    token = str(os.environ["MERAKI_API_KEY"])
    if token in [""]:
        logger.warning('API Key for Meraki is missing. check ENV')
        return False
    else:
        return True
