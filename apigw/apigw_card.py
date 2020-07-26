"""
TECHX API GATEWAY
ADAPTIVE CARDS FOR WEBEX TEAMS
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
"""

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"


# ==== CARD Containers =====
meraki_form = {}
simple_form = {}


# === SIMPLE AdaptiveCard Form in Python Description =====
# ==== Card HEADER ========
simple_form["contentType"] = "application/vnd.microsoft.card.adaptive"
simple_form["content"] = {}
simple_form["content"]["$schema"] = "http://adaptivecards.io/schemas/adaptive-card.json"
simple_form["content"]["type"] = "AdaptiveCard"
simple_form["content"]["version"] = "1.2"
simple_form["content"]["body"] = []
simple_form["content"]["actions"] = []
# ==== Card Components BODY ============
## === Title Component ====
title_comp = {}
title_comp["type"] = "TextBlock"
title_comp["text"] = "Simple Form"
title_comp["weight"] = "bolder"
title_comp["size"] = "medium"
simple_form["content"]["body"].append(title_comp)
## === Input.Text Component ====
input_comp = {}
input_comp["type"] = "Input.Text"
input_comp["id"] = "network_name"
input_comp["placeholder"] = "Network ID"
simple_form["content"]["body"].append(input_comp)
## === Input NUMBER Component ==
numeric_comp = {}
numeric_comp["type"] = "Input.Number"
numeric_comp["id"] = "vlan_id"
numeric_comp["placeholder"] = "VLAN Number"
numeric_comp["min"] = 1
numeric_comp["max"] = 4096
simple_form["content"]["body"].append(numeric_comp)
## === Input TOGGLE Component ==
toggle_comp = {}
toggle_comp["type"] = "Input.Toggle"
toggle_comp["title"] = "Enable port"
toggle_comp["id"] = "enable_port"
toggle_comp["value"] = "true"
simple_form["content"]["body"].append(toggle_comp)
# ==== Card ACTION ==========
## ==== Submit BUTTON Component ===
submit_button = {}
submit_button["type"] = "Action.Submit"
submit_button["title"] = "Submit"
simple_form["content"]["actions"].append(submit_button)
# ===== END OF AdaptiveCard ========


# ==== JSON Format for Adaptive Card
meraki_form = {
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
            {
                "type": "TextBlock",
                "text": "Meraki Vlan Changer",
                "id": "form_title",
                "spacing": "Medium",
                "size": "Medium",
                "weight": "Lighter",
                "color": "Light",
            },
            {
                "type": "Input.Text",
                "placeholder": "IP Address 1.1.1.1",
                "id": "switch_ip",
                "maxLength": 15,
                "spacing": "ExtraLarge",
            },
            {
                "type": "Input.Number",
                "placeholder": "Select Port Number",
                "id": "port_number",
                "min": 1,
                "max": 48,
            },
            {
                "type": "Input.Text",
                "placeholder": "Set Port Name",
                "id": "port_name",
                "maxLength": 20,
                "spacing": "ExtraLarge",
                "separator": True,
            },
            {
                "type": "Input.Text",
                "placeholder": "Set Data Vlan Number",
                "id": "data_vlan",
                "maxLength": 4,
            },
            {
                "type": "Input.Text",
                "placeholder": "Set Voice Vlan",
                "id": "voice_vlan",
                "maxLength": 4,
            },
            {
                "type": "Input.Toggle",
                "title": "Enable",
                "value": "true",
                "wrap": True,
                "separator": True,
                "id": "port_status",
                "spacing": "ExtraLarge",
            },
            {
                "type": "Input.Toggle",
                "title": "Enabling Trunking",
                "value": "false",
                "wrap": False,
                "id": "trunk_status",
            },
            {
                "type": "Input.Toggle",
                "title": "PoE",
                "value": "true",
                "wrap": False,
                "id": "poe_status",
            },
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Apply",
                "id": "submitAction",
                "style": "positive",
            }
        ],
    },
}
