'''
TECHX API GATEWAY
TEST MODULE FOR API GATEWAY
CREATED BY: FRBELLO AT CISCO DOT COM
DATE : JUL 2020
VERSION: 1.0
STATE: RC2
'''

__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2020 Cisco and/or its affiliates."
__license__ = "MIT"

# ==== importing Library ===
import unittest

# === Test Targets =====
import apigw_server
import apigw_generic
import apigw_meraki

# ==== Test Flask Webserver Routes ===
class ApicGWTest(unittest.TestCase):
    '''
    Unit Test for Flask Server
    '''
    def setUp(self):
        '''
        Connection to Flask APP Server
        '''
        apigw_server.app.testing = True
        self.app = apigw_server.app.test_client()

    def test_home_page(self):
        '''
        testing Flask /
        '''
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)


    def test_webex_incoming(self):
        '''
        Testing POST Messages
        '''
        pass


    def tearDown(self):
        '''
        End Testing
        '''
        pass

# ==== Test GENERIC API Gateway ===
class GenericAPITest(unittest.TestCase):
    '''
    UNIT Test for GENERIC API
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

# ==== Test Genral Functions =======
class GenericFuntionsTest(unittest.TestCase):
    '''
    Testing Generic Functions
    '''
    def setUp(self):
        pass

    def test_webext_is_enable(self):
        '''
        Validate WbxT Token Checker Function
        '''
        self.assertTrue(apigw_generic.apigw_webext_enable())
    def tearDown(self):
        pass

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
        self.assertTrue(apigw_meraki.apigw_meraki_api_enable()) 

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
        size_of = 8
        psk = apigw_meraki.generate_preshare_key(size_of)
        self.assertTrue(psk)       


    def tearDown(self):
        pass    

# ==== Main Function ======
if __name__ == '__main__':
    unittest.main()
