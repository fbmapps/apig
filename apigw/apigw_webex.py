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
import logging
from webexteamssdk import WebexTeamsAPI, WebhookEvent, ApiError

# ==== Create a Logger ======
logger = logging.getLogger("apigw.WebexTemas")


def apigw_webex_listener(payload):
    """
    Receive Webhook Callback from Webex Teams
    payload is in JSON
    """
    logger.info("Incoming Message from Webex Teams")

    webex_bot = WebexTeamsAPI()
    webex_rx = WebhookEvent(payload)
    response = {"status_code": 200, "status_info": "success"}

    in_room = webex_bot.rooms.get(webex_rx.data.roomId)
    in_msg = webex_bot.messages.get(webex_rx.data.id)
    in_person = webex_bot.people.get(in_msg.personId)
    my_own = webex_bot.people.me()
    out_msg = ""

    try:
        if in_msg.personId == my_own.id:
            response = {"status_code": 400, "status_info": "Can't message myself"}
            return response
        response = {
            "status_code": 200,
            "status_info": "success",
            "request": in_msg.text,
            "space": in_room.title,
        }
        out_msg = f"""Hi {in_person.firstName}. I've just read your message.
                          \nIt seems you want to **{in_msg.text}**, 
                          \nam I right?
                          """
        logger.info(response)
    except ApiError as err:
        logger.error("Failure in procesing incoming message from Team : %s", err)
        out_msg = "Unable to process the Message"
        response = {"status_code": 400, "status_info": "error"}

    webex_bot.messages.create(in_room.id, markdown=out_msg)
    logger.info("Messsage Dispatch : %s", out_msg)
    return response
