"""
TECHX API GATEWAY
COMMUNICATION WITH WEBEX TEAMS
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
"""
__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"
# ==== Libraries ====
import os
import logging
import yaml
from webexteamssdk import WebexTeamsAPI, WebhookEvent, ApiError
# ==== Custom APIGW Libraries ====
from apigw.apigw_dispatcher import APIGWDispatcher
from apigw.apigw_generic import webex_teams_enable
from apigw.apigw_misc import CovidStats
from apigw.apigw_card import meraki_form, simple_form
from apigw.apigw_meraki import APIGWMerakiWorker, meraki_api_enable
# ==== Create a Logger ======
logger = logging.getLogger("apigw.WebexTeams")

def apigw_webex_listener(payload):
    """
    Receive Webhook Callback from Webex Teams
    payload is in JSON
    """
    logger.info("Incoming Message from Webex Teams")

    # Validate if Callback is from a valid Webex Team Space
    #### BEST PRACTICE FOR Allow Only Traffic of Interest
    source_room = payload["data"]["roomId"]
    if not check_source_room(source_room):
        response = {"status_code": 400, "status_info": "No a Valid Room"}
        return response

    #Retrieve the person Email for Requestor Validation
     #### BEST PRACTICE FOR Allow Only Traffic of Interest
    requestor_email = payload["data"]["personEmail"]
    if not check_requestor_email(requestor_email):
        logger.info("Person is not allowed: %s ", requestor_email)
        response = {"status_code": 400, "status_info": "User is not in Allowance List"}
        return response    
    logger.info("Person is in allowance list: %s ", requestor_email)    

    # If Room is a valid source, then Instatiate the APIG Create all the Objects
    webex_bot = WebexTeamsAPI()
    webex_rx = WebhookEvent(payload)
    dispatcher = APIGWDispatcher(webex_bot)

    # Webex Teams API Objects
    in_room = webex_bot.rooms.get(webex_rx.data.roomId)
    in_msg = webex_bot.messages.get(webex_rx.data.id)
    in_person = webex_bot.people.get(in_msg.personId)
    requestor_name = in_person.displayName
    requestor_orgid = in_person.orgId
    my_own = webex_bot.people.me()
    out_msg = ""

    # Verify is message arrive from a valid Organization
     #### BEST PRACTICE FOR Allow Only Traffic of Interest
    if check_orgid_origin(requestor_orgid):
        logger.info("Organization is allowed")
    else:
        logger.info("Organization is not allowed")
        response = {"status_code": 400, "status_info": "Organization is not Allowed"}
        return response

    # Built the Actions Menu in the APIGWDispatcher
    logger.info("Preparing Actions Menu for APIGWDispatcher for Webex Teams Client for %s", requestor_name)
    if apigw_actions_builder(dispatcher, requestor_name):
        logger.info("Webex Teams Action Menu built sucessfully")
    else:
        logger.error(
            "Action Menu build fails, Default Action is the only opyion available"
        )

    # Start Processing
    response = {"status_code": 200, "status_info": "success"}

    if in_room.type == "direct":
        order_intent = in_msg.text.rstrip()
    else:
        input_str = in_msg.text.split(" ", 1)
        order_intent = input_str[1]

    try:
        if in_msg.personId == my_own.id:
            response = {"status_code": 400, "status_info": "Can't message myself"}
            return response
        out_msg = dispatcher.get_orders(order_intent, in_person, in_room)
        response = {
            "status_code": 200,
            "status_info": "success",
            "request": order_intent,
            "space": in_room.title,
        }
        logger.info(response)
    except ApiError as err:
        logger.error("Failure in procesing incoming message from Team : %s", err)
        out_msg = "**Unable to process the Message**"
        response = {"status_code": 400, "status_info": "error"}

    if apigw_send_message(webex_bot, in_room.id, out_msg):
        logger.info("Messsage Dispatched : %s", out_msg)
    else:
        logger.info("Messsage Delivery Failure")

    # Clean Objects
    del webex_bot
    del dispatcher
    del webex_rx
    logger.info("All Objects references has been cleared out")
    return response

# ====== Helpers Functions ==========

## ========= SECURITY CHECK FUNCTIONS ============
def check_source_room(room_id):
    """
    Helper Function to validate if Space is One:One or Group
    Return True/False
    """
    direct_room = str(os.environ["WEBEX_TEAMS_DIRECT_ROOM"])
    group_room = str(os.environ["WEBEX_TEAMS_GROUP_ROOM"])
    check = False
    if room_id in (direct_room, group_room):
        check = True
    return check

def check_orgid_origin(msg_orgid):
    """
    Check ORGID from the Job Requester from Webex
    receive REQ_ORGID
    return: True/False
    WEBEX BEST PRACTICE
    /blog/building-a-more-secure-bot
    """
    comm_allowed = False
    bot_orgid = str(os.environ['WEBEX_ALLOWED_ORGANIZATION'])
    if bot_orgid == msg_orgid:
        comm_allowed = True
    return comm_allowed

def check_requestor_email(person_email):
    """
    Check personEmail from the Job Requester from Webex
    receive personEmail from webhook message
    return: True/False
    WEBEX BEST PRACTICE
    /blog/building-a-more-secure-bot
    """
    comm_allowed = False
    with open('allowed_users.yaml', 'r') as stream:
        data = yaml.safe_load(stream)
        if person_email in str(data["Allowed"]["email"]):
            comm_allowed = True
    return comm_allowed
### =================== END OF SECURITY ===============

## ====== General Purpuose Functions ========
def get_health(message):
    """
    Simple Health Check
    params
    message: incoming message
    return: True/False
    """
    if message:
        health_check = "Webex Teams Comm is Working :) "
    else:
        health_check = " Webex Teams Comm is not working :("
    return health_check


def apigw_send_message(webex_bot, room_id, message, card=None):
    """
    DRY for Message delivery
    """
    delivery_status = False
    try:
        if card is None:
            webex_bot.messages.create(room_id, markdown=message)
        else:
            webex_bot.messages.create(room_id, text=message, atachments=card)
        delivery_status = True
    except ApiError:
        delivery_status = False
    return delivery_status
def send_card(message):
    """
    Send an AdaptiveCard
    """
    return meraki_form

def simple_card(message):
    """
        Send an AdaptiveCard
        """
    return simple_form

# Generic Action Registrar
def apigw_actions_builder(dispatcher, requestor_name):
    """
    Create the Menu Actions based on Enabled Services
    params:
    Registrar - APIGWDispatcher Object
    Requester -  Person sending the message
    ActionSet - The Action Array (action-word, halper-msg, command)
    return: True/False
    """
    action_builder = False

    if webex_teams_enable():
        dispatcher.add_action(
            "webex-health", "Get Health of Webex Teams Link", get_health
        )
        dispatcher.add_action("send-card", "Send Meraki Form", send_card)
        dispatcher.add_action("simple-card", "Adaptive Card Simple form", simple_card)

        action_builder = True
    
    # Meraki Service
    if meraki_api_enable():
        mki = APIGWMerakiWorker(requestor_name)
        dispatcher.add_action(
                "show-network",
                "Summary Info of Managed Meraki Network",
                mki.show_meraki_network
                )
        dispatcher.add_action(
                "show-vlans",
                "Display a List with the VLANS attached to the Meraki Network",
                mki.show_meraki_vlans
                )
        dispatcher.add_action(
                "show-switch",
                "Display a List with the Switches attached to the Meraki Network",
                mki.show_meraki_switch
                )
        dispatcher.add_action(
                "change-port",
                "Parameters: Switch IP, Switch-Port, Vlan-ID ie _change-port 1.1.1.1 10 101_",
                mki.change_port_vlan
                )
        dispatcher.add_action(
                "activate-ssid",
                "Parameters: SSID Name, ie _activate-ssid SSIDName_",
                mki.activate_new_ssid
                )        
        dispatcher.add_action(
                "show-ssid",
                "Parameters: Display a List of All Enabled SSIDs",
                mki.show_meraki_ssid
                ) 
        dispatcher.add_action(
                "remove-ssid",
                "Parameters: Remove and Disable a SSIDs by name or Number ID ie _remove-ssid <SSID NAME> | <SSID NUMBER 1 to 15>_",
                mki.remove_ssid
                )   
        dispatcher.add_action(
                "show-ports",
                "Parameters: Display All Ports in a Switch _show-ports <Switch IP>_",
                mki.show_meraki_ports
                )                
        dispatcher.add_action(
                "show-mx-ports",
                "Parameters: Display All Ports in a MX appliance _show-mx-ports_",
                mki.show_meraki_mx_ports
                )
        dispatcher.add_action(
                "disable-port",
                "Parameters: Deactivate Switch Port _diasble-port <IP_ADDR> <PORT_ID>_",
                mki.deactivate_port
                )          

    # Sample Service
    covid = CovidStats()
    dispatcher.add_action(
        "covid-info", "Latest-Covid Information", covid.get_covid_summary
    )
    return action_builder