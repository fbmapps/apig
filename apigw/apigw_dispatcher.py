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


# ==== Service API Fucntions ========

# ==== Class Blue Print ====
class APIGWDispatcher:
    """
    Class to Receive Order Requests and Call Specific Resources
    """
    def __init__(self, webex_bot):
        self.__name__ = "APIGW_Dispatcher"
        self.webex_bot = webex_bot
        self.actions = {"help": {"help": "Get Help", "callback": self.send_help}}

    def get_orders(self, order_intent, person, room):
        """
        Collect Order Intent from message and
        pass to the specific worker
        """
        # ===== Inputs =======
        in_message = order_intent
        # ==== Outputs ======
        out_msg = ""

        logger.info("Order Intent Processing Start : %s", in_message)

        # ====
        if room.type == "direct":
            # If Request came from a 1-to-1 no mention is needed
            order_rx_msg = "Ok. I got your order. let me check the actions available..."
        else:
            # if requests came from a Space, then you can mention the requester
            order_rx_msg = f"""Hi <@personId:{person.id}>.  \n
                           I have your order in queue.  \n
                           Please, Let me check the actions available...  \n
                           """
        # Send the message
        logger.info("Order Acknowledege sended")
        self.webex_bot.messages.create(room.id, markdown=order_rx_msg)

        # Extract the Action
        logger.info("Start Action parsing and processing : %s", in_message)
        action = ""
        for item in self.actions.items():
            if in_message.find(item[0]) != -1:
                # If Not Empty
                action = item[0]
                # At Least an action exist
                logger.info("Dispatcher has Actions configured")
                # Stop looking more actions
                break

        # Execute the action
        # If there is not action send help
        if action in [""]:
            logger.warning(
                "No action defined for: %s. Help Information dispatched", in_message
            )
            out_msg = self.actions["help"]["callback"](in_message)
        elif action in self.actions.keys():
            logger.info("A configured Action has been received: %s", action)
            if "card" in action:
                logger.info("An AdaptiveCard is enclosed in the message")
                reply = []
                rx_dict = self.actions[action]["callback"](in_message)
                reply.append(rx_dict)
                out_msg = "AdaptiveCard Enclosed"
                self.webex_bot.messages.create(room.id, markdown=out_msg, attachments=reply)
            else:
                #Regular Message
                out_msg = self.actions[action]["callback"](in_message)
        else:
            logger.warning("No Match with an defined Action: %s", action)
   
        logger.info("Order Intent Proccess finish. Action   : %s ", in_message)
        return out_msg

    def add_action(self, action, help_message, callback):
        """
        Add a New command to the Dispatcher
        params:
        action: string for call to action ie, /changevlan
        help: the help message describing the action
        callback: the function to invoke
        return:
        """
        self.actions[action] = {"help": help_message, "callback": callback}

    def remove_action(self, action):
        """
        Remove an Action from Actions List
        params
        action: Action to be removed
        return:
        """
        del self.actions[action]

    def send_help(self, in_message):
        """
        A Simple Help Message for Users
        params:
        post_data
        return: message
        """
        message = f"Hello, you send **{in_message}**  \n"
        message += "and I am ready to only understand the following actions:  \n"

        for item in self.actions.items():
            if item[1]["help"] != "*":
                message += "* **%s**: %s  \n" % (item[0], item[1]["help"])
        return message

    def extract_message(self, action, text):
        """
        Return message contents following a given command.
        :param command: Command to search for.  Example "/echo"
        :param text: text to search within.
        :return:
        """
        cmd_loc = text.find(action)
        message = text[cmd_loc + len(action) :]
        return message