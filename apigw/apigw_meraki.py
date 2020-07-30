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
import secrets
import string
import re
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
        check_icon = chr(0x2705)
        vlan_count = 0
        message = f"There are {len(data)} vlans in the Network. Details:  \n"
        for vlan in data:
            message += f"* **{vlan['name']}** |  ID: **{vlan['id']}** | Subnet: **{vlan['subnet']}**  \n"
            vlan_count += 1
        message += f" {check_icon} Total: **{vlan_count}**  \n" 
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
        check_icon = chr(0x2705)
        for device in data:
            device_type = decode_meraki_model(device["model"])
            if "switch" in device_type:
                message += f"* **{device['name']}** |  IP: **{device['lanIp']}** | Serial: **{device['serial']}**  \n"
                device_counter += 1
        message += f"{check_icon} Total: **{device_counter}**  \n"        
        return message

    def show_meraki_mx_ports(self, job_req):
        """
        Show Ports Associated to MX Meraki Device
        job_req: Message from Dispatcher, parse the request
        device_type = mx, ms, mv, mr, mc, wireless, switch, appliance
        return a message
        API V1
        """
        logger.info("Job Received : %s", job_req)
        api_uri = f"/v1/networks/{self.meraki_net}/appliance/ports"
        data = get_meraki_api_data(api_uri)
        # Parse the JSON
        message = "Here is the detail:  \n"
        port_counter = 0
        check_icon = chr(0x2705)
        for mx_port in data:
            message += f"* **{mx_port['number']}** |  Port Mode: **{mx_port['type']}** | Vlan ID: **{mx_port['vlan']}**  \n"
            port_counter += 1
        message += f"{check_icon} Total: **{port_counter}**  \n"        
        return message    

    def show_meraki_ports(self, job_req):
        """
        Retrieve all Ports from a Switch
        """
        logger.info("Job Received : %s", job_req)
        fails_icon = chr(0x2757) + chr(0xFE0F)
        check_icon = chr(0x2705)
        message = ""
        job_params = job_req.split()
        if len(job_params) < 2:
            #Not Enough info provided
            message = f" {fails_icon} Job Request is incomplete, please provide Switch IP _show-ports <SWITCH_IP>_ \n"
        else:
            ## STEP 0-1: Assign all the parameters to job variables
            ip_addr = job_params[1]
            serial_id, switch_name = get_switch_serial(ip_addr, self.meraki_net)
            if serial_id in [""]:
                message = f"{devicon} **There is not switch with that IP**"
                logger.error("VALIDATION failed Switch serial not Found %s", ip_addr)
                return message
            else:
                logger.info("VALIDATION Succeeded Switch serial Found %s", serial_id)

            # STEP 1 - Retrieve Data    
            api_uri = f"/v1/devices/{serial_id}/switch/ports/"
            data = get_meraki_api_data(api_uri)
            port_counter = 0
            message = f"Here is the detail for {switch_name}  \n"
            for port in data:
                message += f"* Port **{port['portId']}** |  Type : **{port['type']}** | VLAN: **{port['vlan']}** | VoiceVlan **{port['voiceVlan']}**  \n"
                port_counter += 1
            message += f"{check_icon} Total Ports: **{port_counter}**  \n"
        return message

    def show_meraki_ssid(self, job_req):
        """
        Show All enabled and named SSID
        job_req: Message from Dispatcher, parse the request
        API V1
        """
        message = ""
        logger.info("Job Received : %s", job_req)
        api_uri = f"/v1/networks/{self.meraki_net}/wireless/ssids"
        data = get_meraki_api_data(api_uri)
        message = "Here is the detail:  \n"
        configured_ssid_counter = 0
        unused_ssid_counter = 0
        check_icon = chr(0x2705)
        for ssid in data:
            # Find Enabled SSID first
            if ssid["enabled"]:
                message += f"* Enabled SSID: ({ssid['number']}) **{ssid['name']}** Mode **{ssid['authMode']}**  \n"
                configured_ssid_counter += 1
            # Find Named SSID which are disabled
            # Extract SSID Name
            ssid_cur_name = ssid["name"].split()
            if "Unconfigured" not in [ssid_cur_name[0].strip()] and not ssid["enabled"]:
                message += f"* Disbaled SSID ({ssid['number']}) **{ssid['name']}** Mode **{ssid['authMode']}**  \n"
                configured_ssid_counter += 1
            else:
                # All the Unconfigured SSIDs
                unused_ssid_counter += 1

        message += f"{check_icon} Total: Configured **{configured_ssid_counter}** Unused **{unused_ssid_counter - configured_ssid_counter }**  \n"
        return message        

    def change_port_vlan(self, job_req):
        """
        Change a Switch Port and assign a vlan
        params:
        job_req: Message from Dispatcher
        return: Job Action Message
        API V1
        """
        # STEP-0 Extract parameters from job_req
        #job_params
        #job_params[0]: Bot Command
        #job_params[1]: Switch IP Address
        #job_params[2]: Port Number
        #job_params[3]: Vlan ID
        devicon = chr(0x2757) + chr(0xFE0F)
        check_icon = chr(0x2705)
        job_params = job_req.split()
        if len(job_params) < 4:
            #Not Enough info provided
            message = f" Job Request is incomplete, please provide Switch IP, Switch-Port, Vlan-ID ie _change-port-vlan 1.1.1.1 10 101 \n"
        else:
            ## STEP 0-1: Assign all the parameters to job variables
            ip_addr = "".join(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', job_params[1])) #Validate IP Addr. Format
            port_id = "".join(re.findall(r'^\d{1,2}$',job_params[2])) # Accept upto 2 Digits
            vlan_id = "".join(re.findall(r'^\d{1,4}$',job_params[3])) #Accept up to 4 Digits


            # STEP 1: Validations
            ## STEP 1-1: GET Switch Serial Number
            serial_id, switch_name = get_switch_serial(ip_addr, self.meraki_net)
            if serial_id in [""]:
                message = f"{devicon} **There is not switch with that IP**"
                logger.error("VALIDATION failed Switch serial not Found %s", ip_addr)
                return message
            else:
                logger.info("VALIDATION Succeeded Switch serial Found %s", serial_id)

            ## STEP 1-2: Validate Vlans ID
            vlan_exists, vlan_name = validate_vlan(vlan_id, self.meraki_net)
            if vlan_exists:
                logger.info("VALIDATION Succeeded Vlan ID Valid for %s Name: %s", vlan_id, vlan_name)
            else:
                logger.error("VALIDATION failed Vlan ID not Found %s", vlan_id)
                message = f"{devicon} **Invalid VLAN ID**"
                return message

            ## STEP 1-3: Validate Port ID
            if validate_port(port_id, serial_id):
                logger.info("VALIDATION Succeeded Port ID Valid %s", port_id)
            else:
                logger.error("VALIDATION failed Port ID not Found %s", port_id)
                message = f"{devicon} **Invalid Port ID**"
                return message

            # STEP 2: Prepare the Payload
            port_payload = {}
            port_payload["name"] = f"Port changed by {self.job_owner} to {vlan_name.upper()} via Teams"
            port_payload["tags"] = ["Changed","Automation", "WebexBot", "DevOps"]
            port_payload["vlan"] = vlan_id
            port_payload["type"] = "access"
            port_payload["enabled"] = True
            logger.info("JSON Data to Port Update %s ", json.dumps(port_payload))

            # STEP 3: Send The Change to API
            api_uri = f"/v1/devices/{serial_id}/switch/ports/{int(port_id)}"
            data = update_via_meraki_api(api_uri, port_payload)
            if data:
                logger.info("Port updated successfully job_owner %s : ", self.job_owner)
                message = f" {check_icon} **Port Update has been applied Sucesfully**  \n"
                message += F"* Job Owner: **{self.job_owner}**  \n"
                message += F"* Switch Name: **{switch_name}**  \n"
                message += f"* PortID **{data['portId']}**  \n"
                message += f"* Port Name **{data['name']}**  \n"
                message += f"* Port Type **{data['type']}**  \n"
                message += f"* VLAN ID **{data['vlan']}**  \n"
                message += f"* Voice Vlan **{data['voiceVlan']}**  \n"
            else:                
                logger.error("Port update failed : ") 
                message = f"{devicon} Port Update incomplete"
        return message 

    def deactivate_port(self, job_req):
        """
        Change a Switch Port and assign a vlan
        params:
        job_req: Message from Dispatcher
        return: Job Action Message
        API V1
        """
        # STEP-0 Extract parameters from job_req
        #job_params
        #job_params[0]: Bot Command
        #job_params[1]: Switch IP Address
        #job_params[2]: Port Number
        devicon = chr(0x2757) + chr(0xFE0F)
        check_icon = chr(0x2705)
        job_params = job_req.split()
        if len(job_params) < 3:
            #Not Enough info provided
            message = f" Job Request is incomplete, please provide Switch IP, Switch-Port, Vlan-ID ie _change-port-vlan 1.1.1.1 10 101 \n"
        else:
            ## STEP 0-1: Assign all the parameters to job variables
            ip_addr = "".join(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', job_params[1])) #Well Formed IP Address
            port_id = "".join(re.findall(r'^\d{1,2}$',job_params[2])) #Accepting up to numbers
            # STEP 1: Validations
            ## STEP 1-1: GET Switch Serial Number
            serial_id, switch_name = get_switch_serial(ip_addr, self.meraki_net)
            if serial_id in [""]:
                message = f"{devicon} **There is not switch with that IP**"
                logger.error("VALIDATION failed Switch serial not Found %s", ip_addr)
                return message
            else:
                logger.info("VALIDATION Succeeded Switch serial Found %s", serial_id)

            ## STEP 1-2: Validate Port ID
            if validate_port(port_id, serial_id):
                logger.info("VALIDATION Succeeded Port ID Valid %s", port_id)
            else:
                logger.error("VALIDATION failed Port ID not Found %s", port_id)
                message = f"{devicon} **Invalid Port ID**"
                return message

            # STEP 2: Prepare the Payload
            port_payload = {}
            port_payload["name"] = f"Port disabled by {self.job_owner} via Teams"
            port_payload["enabled"] = False
            logger.info("JSON Data to Port Update %s ", json.dumps(port_payload))

            # STEP 3: Send The Change to API
            api_uri = f"/v1/devices/{serial_id}/switch/ports/{int(port_id)}"
            data = update_via_meraki_api(api_uri, port_payload)
            if data:
                logger.info("Port updated successfully job_owner %s : ", self.job_owner)
                message = f" {check_icon} **Port Update has been applied Sucesfully**  \n"
                message += F"* Job Owner: **{self.job_owner}**  \n"
                message += F"* Switch Name: **{switch_name}**  \n"
                message += f"* PortID **{data['portId']}**  \n"
                message += f"* Port Name **{data['name']}**  \n"
                message += f"* Port Type **{data['enabled']}**  \n"
            else:                
                logger.error("Port update failed : ") 
                message = f"{devicon} Port Update incomplete"
        return message

    def activate_new_ssid(self, job_req):
        """
        Select Unused SSID and Activate it for Services
        params: job_req - Message from Dispacther with job details
        return: Message Confirmation
        API V0
        """
        message = ""
        devicon = chr(0x2757) + chr(0xFE0F)
        check_icon = chr(0x2705)
        # STEP-0 Extract parameters from job_req
        job_params = job_req.split(" ", 1)
        ## job_params[0] = Bot Command
        ## job_params[1] = SSID Name
        ## STEP 0-1 job_req validation
        if len(job_params) < 2:
            #Not Enough info provided
            message = "Job Request is incomplete, please provide SSID Name ie. _activate-ssid Testing_  \n"
        else:
            ## STEP 0-2 Assign job_params to job variables
            ssid_name = job_params[1]
            # STEP 1 - Get the First Unused SSID
            ssid_num, ssid_state = get_unused_ssid(self.meraki_net)
            if ssid_num == -1:
                message = f"{devicon} **All SSID are in Use**"
                logger.error("VALIDATION failed Not Available SSID to Activate")
                return message
            else:
                logger.info("VALIDATION succeeded the SSID number %s is available", str(ssid_num).strip())

            # STEP 2 - Prepare Payload:
            ssid_payload = {}
            ssid_payload["name"] = ssid_name.strip()
            ssid_payload["enabled"] = True
            ssid_payload["authMode"] = "psk"
            ssid_payload["encryptionMode"] = "wpa"
            ssid_payload["wpaEncryptionMode"] = "WPA2 only"
            ssid_payload["visible"] = True
            ssid_payload["psk"] = generate_preshare_key()

            # STEP 3 - Request Activation to Meraki API:
            api_uri = f"/v0/networks/{self.meraki_net}/ssids/{ssid_num}"
            data = update_via_meraki_api(api_uri, ssid_payload)
            if data:
                logger.info("SSID Activation succeeded for job_owner %s : ", self.job_owner)
                message = f" {check_icon} **SSID Activation has been applied sucesfully**  \n"
                message += F"* Job Owner: **{self.job_owner}**  \n"
                message += f"* SSID Number **{data['number']}**  \n"
                message += f"* SSID Name **{data['name']}**  \n"
                message += f"* Preshare Key **{data['psk']}**  \n"
                message += f"* Encryption Mode **{data['encryptionMode']}**  \n"
                message += f"* Visible **{data['visible']}**  \n"
            else:                
                logger.error("SSID Activation failed : ") 
                message = f"{devicon} **SSID Activation incomplete**"

        return message

    def remove_ssid(self, job_req):
        """
        Select Unused SSID and Activate it for Services
        params: job_req - Message from Dispacther with job details
        return: Message Confirmation
        API V0
        """
        message = ""
        devicon = chr(0x2757) + chr(0xFE0F)
        check_icon = chr(0x2705)
        # STEP-0 Extract parameters from job_req
        job_params = job_req.split(" ", 1)
        ## job_params[0] = Bot Command
        ## job_params[1] = SSID Name
        ## STEP 0-1 job_req validation
        if len(job_params) < 2:
            #Not Enough info provided
            message = "Job Request is incomplete, please provide SSID Name ie. _remove-ssid Testing_  \n"
        else:
            ## STEP 0-2 Assign job_params to job variables
            if str(job_params[1]).isnumeric():
                # The Job Owner Submit already a SSID Number
                ssid_num = int(job_params[1])
                logger.info("VALIDATION succeeded SSID number %s  provided by %s", ssid_num, self.job_owner)

            else:
                ## STEP 0-3 Get SSID ID
                # The Job Owner pass a name so a ssid_number should be retrieve
                ssid_name = str(job_params[1]).strip()
                ssid_num = get_used_ssid_by_name(self.meraki_net, ssid_name)
                logger.info("VALIDATION succeeded SSID number %s for %s ", str(ssid_num) , ssid_name)

            # STEP 2 - Prepare Payload:
            ssid_payload = {}
            ssid_payload["name"] = "Unconfigured SSID " + str(ssid_num + 1)
            ssid_payload["enabled"] = False
            ssid_payload["authMode"] = "open"
            ssid_payload["visible"] = True

            # STEP 3 - Request Deactivation to Meraki API:
            api_uri = f"/v0/networks/{self.meraki_net}/ssids/{ssid_num}"
            data = update_via_meraki_api(api_uri, ssid_payload)
            if data:
                logger.info("SSID removal succeeded for job_owner %s : ", self.job_owner)
                message = f"{check_icon} **SSID Deactivation has been completed sucesfully**  \n"
                message += F"* Job Owner: **{self.job_owner}**  \n"
                message += f"* SSID Number **{data['number']}**  \n"
                message += f"* SSID Name **{data['name']}**  \n"
                message += f"* Authentication **{data['authMode']}**  \n"
                message += f"* Visible **{data['visible']}**  \n"
            else:                
                logger.error("SSID Deactivation failed : ") 
                message = f"{devicon} **SSID Deactivation incomplete**"
        
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

def post_via_meraki_api(api_uri, payload):
    """
    PUT Task sended to Meraki
    api_uri = resource endpoint
    api_header = special header with api_key
    payload = Data to Update, conforming API format 
    """
    url = API_URL + api_uri
    post_data = json.dumps(payload)
    make_post = requests.post(url, headers=api_headers, data=post_data, verify=False)
    if make_post.status_code in [200, 201, 202, 203, 204]:
        data = json.loads(make_update.text)
        logger.info("Meraki POST operation suceeded : %s ", api_uri)
    else:
        data = {}
        logger.info("Meraki POST Operation failed : %s", make_update.status_code)
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
    APIV1
    """
    serial_id = ""
    api_uri = f"/v1/networks/{meraki_net}/devices"
    data = get_meraki_api_data(api_uri)
    for device in data:
        device_type = decode_meraki_model(device["model"])
        if "switch" in device_type: 
            if ip_addr in device["lanIp"]:
                serial_id = str(device["serial"]).strip()
                switch_name = str(device["name"]).strip()
                logger.info("Switch Found! Serial %s" , serial_id)            
    return serial_id, switch_name

def get_unused_ssid(meraki_net):
    ssid_num = -1
    ssid_state = False
    api_uri = f"/v1/networks/{meraki_net}/wireless/ssids"
    data = get_meraki_api_data(api_uri)
    for ssid in data:
        current_label = str(ssid["name"]).split()[0] # Extract the First Word of the SSID Label
        if "Unconfigured" in [current_label]:
            ssid_num = ssid["number"]
            ssid_state = ssid["enabled"]
            print(ssid["name"])
            break #Stop at the First SSID Unused
            
    return ssid_num, ssid_state

def get_used_ssid_by_name(meraki_net, ssid_name):
    ssid_num = -1
    api_uri = f"/v1/networks/{meraki_net}/wireless/ssids"
    data = get_meraki_api_data(api_uri)
    for ssid in data:
        current_label = str(ssid["name"]).strip() # Extract the First Word of the SSID Label
        if ssid_name in [current_label]:
            ssid_num = ssid["number"]
            break #Stop at the First SSID Unused
            
    return ssid_num    

def generate_preshare_key(size_of_psk=16):
    """
    Random Preshare Key Generator
    Use Secrets to Generate Cryptographic Unique PSK
    params: size_of_psk - Number of Characters to generate Default 16 Characters
    return: Preshare Key
    """
    preshare_key = ""
    psk_source = string.ascii_letters + string.digits
    for i in range(size_of_psk):
        preshare_key += secrets.choice(psk_source)
    
    char_list = list(preshare_key)
    secrets.SystemRandom().shuffle(char_list)
    preshare_key = ''.join(char_list)

    return preshare_key

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