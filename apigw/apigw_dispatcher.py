"""
TECHX API GATEWAY
COMMAND GETTER AND JOB DISPATCHER
RECEIVE MESSAGE AND SEND TO THE WORKER
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
"""

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"

# === Libraries ====
import logging

# === Create Logger ====
logger = logging.getLogger("apigw.DISPATCHER")

# ==== Class Blue Print ====
class APIGWDispatcher:
    """
    Class to Receive Order Requests and Call Specific Resources
    """

    def __init__(self, webex_bot):
        self.__name__ = "APIGW_Dispatcher"
        self.webex_bot = webex_bot

    def get_orders(self, order_intent, person, room):
        """
        Collect Order Intent from message and
        pass to the specific worker
        """

        # ===== Inputs =======
        in_message = order_intent

        # ==== Outputs ======
        out_msg = ""

        logger.info("Order Intent Processing Start : %s" , in_message  )

        # ====
        if room.type == 'direct':
            #If Request came from a 1-to-1 no mention is needed
            order_rx_msg = f'Ok. I got your order. I will do that for you'
        else:
            #if requests came from a Space, then you can mention the requester
            order_rx_msg = f"""Hi <@personId:{person.id}>.
                           \nI have your order in queue.
                           \nPlease, standby while I do that for you
                           """
        #Send the message                   
        self.webex_bot.messages.create(room.id, markdown=order_rx_msg)

        logger.info("Order Intent Proccess finish. Command  : %s ", in_message)

        return out_msg
