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
meraki_api_token = str(os.environ['MERAKI_API_KEY'])
webext_access_token = str(os.environ['WEBEXT_ACCESS_TOKEN'])

# ==== General Functions ===
def apigw_meraki_enable():
    '''
    Validate if Meraki API Token is present
    '''
    if meraki_api_token:
        return True
    else:
        return False

    return False

def apigw_webext_enable():
    '''
    Validate Webex Teams Bot requires data is present
    '''
    if webext_access_token:
        return True
    else:
        return False
    return False
