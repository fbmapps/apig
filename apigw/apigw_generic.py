'''
TECHX API GATEWAY 
API GATEWAY GENERAL CONFIGURATIONS
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
'''

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"

# ===== Libraries ========
import os

# ==== Load ENV Variables ===
webext_access_token = str(os.environ['WEBEX_TEAMS_ACCESS_TOKEN'])

# ==== General Functions ===
def webex_teams_enable():
    '''
    Validate Webex Teams Bot requires data is present
    '''
    if webext_access_token:
        return True
    else:
        return False
    return False
