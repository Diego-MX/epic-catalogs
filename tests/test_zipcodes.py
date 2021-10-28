from pathlib import Path
from unittest import TestCase, main as unit_main
import requests
import re

from requests import status_codes

class TestZipcodes(TestCase): 
    def set_example(self, has_nbhd=True):
        if has_nbhd:
            example_request = { 
                "input"     : {
                    "neighborhoodsRequest": {
                        "zipcode": "92773"
                }}, 
                "output"    : {
                    "neighborhoodsResponse": {
                        "zipcode": {
                            "code": "92773", 
                            "state": "Veracruz", 
                            "municipality": "Tuxpan"},
                        "neighborhoods": {
                            "numberOfNeighborhoods": "17", 
                            "neighborhoodsPagination": False
            } } } }
        else:
            example_request = { 
                "input"     : {
                    "neighborhoodsRequest": {
                        "zipcode": "01025" }, 
                "output"    : {
            } } }
        return example_request

    def test_base_request_with_tag(self): 
        response = requests.get(URL)
        self.assertEqual(response.status_code, 200)


    def test_simple_request_is_successful(self):
        sample   = self.set_example(has_nbhd=True)
        response = requests.post(f"{URL}/get-zipcode-neighborhoods", json=sample["input"])
        self.assertEqual(response.status_code, 200)


    def test_no_zipcodes_returns_404(self): 
        sample   = self.set_example(has_nbhd=False)
        response = requests.post(f"{URL}/get-zipcode-neighborhoods", json=sample["input"])
        self.assertEqual(response.status_code, 404)



if __name__ == "__main__": 
    import sys
    import config
    
    ENV = config.DEFAULT_ENV if len(sys.argv) == 1 else sys.argv.pop()
    URL = config.ENV_URLS.get(ENV)

    unit_main()

if False:
    from importlib import reload
    from tests import test_zipcodes
    import config

    ENV = "staging" # "local" #
    URL = config.ENV_URLS[ENV]
    
    reload(test_zipcodes)
    
    some_test  = test_zipcodes.TestZipcodes() 
    setup_json = some_test.yes_example()
    an_input   = setup_json["input"]
    a_request  = an_input["neighborhoodsRequest"]
    
    a_response = requests.post(URL, json=an_input)

    a_response.status_code
    print(a_response.text)
    

    