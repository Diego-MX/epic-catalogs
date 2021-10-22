from unittest import TestCase, main as unit_main
from datetime import datetime as dt 
import requests


class TestZipcodes(TestCase): 
    def yes_example(self):
        example_request = { 
                "input"     : {
                    "neighborhoodsRequest": {
                        "zipcode": "92773" }, 
                "output"    : {
                    "neighborhoodsResponse": {
                        "zipcode": {
                            "code": "92773", 
                            "state": "Veracruz", 
                            "municipality": "Tuxpan"},
                        "neighborhoods": {
                            "numberOfNeighborhoods": "17", 
                            "neighborhoodsPagination": False
        } } } } }
        return example_request

    def no_example(self):
        example_request = { 
                "input"     : {
                    "neighborhoodsRequest": {
                        "zipcode": "01025" }, 
                "output"    : {
        } } }
        return example_request


    def test_simple_request_is_successful(self):
        sample   = self.yes_example()
        response = requests.post(URL, json=sample["input"])
        self.assertEqual(response.status_code, 200)


    def test_no_zipcodes_returns_404(self): 
        sample   = self.no_example()
        response = requests.post(URL, json=sample["input"])
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

    ENV = "local" # "local" #
    URL = config.ENV_URLS["ENV"]
    
    reload(test_zipcodes)
    
    some_test  = test_zipcodes.TestZipcodes() 
    setup_json = some_test.yes_example()
    an_input   = setup_json["input"]
    a_request  = an_input["neighborhoodsRequest"]
    
    a_response = requests.post(URL, json=an_input)

    a_response.status_code
    print(a_response.text)
    

    