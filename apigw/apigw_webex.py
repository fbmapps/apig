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
from webexteamssdk import WebexTeamsAPI, WebhookEvent, ApiError

# ==== Custom APIGW Libraries ====
from apigw.apigw_dispatcher import APIGWDispatcher

# ==== Create a Logger ======
logger = logging.getLogger("apigw.WebexTeams")


def apigw_webex_listener(payload):
    """
    Receive Webhook Callback from Webex Teams
    payload is in JSON
    """
    logger.info("Incoming Message from Webex Teams")

    # Validate if Callback is from a valid Webex Team Space
    source_room = payload["data"]["roomId"]

    if not apigw_check_source_room(source_room):
        response = {"status_code": 400, "status_info": "No a Valid Room"}
        return response

    # If Room is a valid source, then Instatiate the APIG
    webex_bot = WebexTeamsAPI()
    webex_rx = WebhookEvent(payload)
    response = {"status_code": 200, "status_info": "success"}

    in_room = webex_bot.rooms.get(webex_rx.data.roomId)
    in_msg = webex_bot.messages.get(webex_rx.data.id)
    in_person = webex_bot.people.get(in_msg.personId)
    my_own = webex_bot.people.me()
    out_msg = ""

    if in_room.type == 'direct':
        order_intent = in_msg.text.rstrip()
    else:
       input_str = in_msg.text.split(' ', 1)
       order_intent = input_str[1]


    try:
        if in_msg.personId == my_own.id:
            response = {"status_code": 400, "status_info": "Can't message myself"}
            return response
        dispatcher = APIGWDispatcher(webex_bot)
        out_msg = dispatcher.get_orders(order_intent, in_person, in_room)
        response = {
            "status_code": 200,
            "status_info": "success",
            "request": order_intent,
            "space": in_room.title,
        }
        #out_msg = f"""Hi {in_person.firstName}. I've just read your message.
        #                  \nIt seems you want to **{in_msg.text}**, 
        #                  \nam I right?
        #                  """
        logger.info(response)
    except ApiError as err:
        logger.error("Failure in procesing incoming message from Team : %s", err)
        out_msg = "**Unable to process the Message**"
        response = {"status_code": 400, "status_info": "error"}

    if apigw_send_message(webex_bot, in_room.id, out_msg):
        logger.info("Messsage Dispatched : %s", out_msg)
    else:
        logger.info("Messsage Delivery Failure")
    return response

# ====== Helpers Functions ==========
def apigw_check_source_room(room_id):
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

def apigw_send_message(webex_bot,room_id, message):
    '''
    DRY for Message delivery
    '''
    delivery_status = False
    try:
        webex_bot.messages.create(room_id, markdown=message)
        delivery_status = True
    except ApiError:
        delivery_status = False
    return delivery_status
