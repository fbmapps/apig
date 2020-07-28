"""
TECHX API GATEWAY
TEST MODULE FOR API GATEWAY
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
"""

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"

# ==== importing Library ===
import os
import unittest

# === Test Targets =====
import apigw_meraki

# ==== Global Values
meraki_net = str(os.environ["MERAKI_DEFAULT_NETWORK"])
meraki_org = str(os.environ["MERAKI_ORG"])

# ==== Meraki Worker Module Tests =======
class MerakiWorkerTest(unittest.TestCase):
    """
    Testing Functionalities in Meraki Module
    """

    def setUp(self):
        pass

    def test_meraki_api_enable(self):
        """
        Validate Meraki Checker Function
        """
        self.assertTrue(apigw_meraki.meraki_api_enable())

    def test_decode_meraki_model(self):
        """
        Validate Meraki Decoder returns the appropiate Value
        """
        label = apigw_meraki.decode_meraki_model("MS220-8P")
        self.assertEqual(label, "switch")

    def test_generate_preshare_key(self):
        """
        Validate Preshare Key Generator
        """
        size_of = 12
        psk = apigw_meraki.generate_preshare_key(size_of)
        self.assertTrue(psk)

    def test_get_unused_ssid(self):
        """
        Check Meraki Function to retrieve the first unused SSID
        """
        ssid_number, ssid_status = apigw_meraki.get_unused_ssid(meraki_net)
        print(ssid_number)
        print(ssid_status)
        #Evaluate first the SSID number and then SSID status
        self.assertTrue( 0 <= ssid_number <= 14, "SSID Out of Range" ) # Check SSID is between 0 and 15
        self.assertEqual(ssid_status, False, "SSID Unavailable") # Check SSID is Disable = enabled : false

    def test_get_used_ssid_by_name(self):
        """
        Check Meraki function to retrieve the current ID from SSID name
        """
        ssid_name = "TestingSSID"
        ssid_number, ssid_status = apigw_meraki.get_used_ssid_by_name(meraki_net, ssid_name)
        self.assertTrue( 0 <= ssid_number <= 14, "SSID Out of Range" ) # Check SSID is between 0 and 15
       

    def tearDown(self):
        pass


# ==== Main Function ======
if __name__ == "__main__":
    unittest.main()
