from pathlib import Path
from unittest import TestCase, main as unit_main
import requests


def set_example(name=None):
    if name is None:
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
    elif name == "no-nbhd":
        example_request = { 
            "input"     : {
                "neighborhoodsRequest": {
                    "zipcode": "01025" }, 
            "output"    : {
        } } }
    elif name == "no-city": 
        example_request = { 
            "input"     : {
                "neighborhoodsRequest": {
                    "zipcode": "54200" 
        } },  
            "output"    : {
        } }
    return example_request


class TestZipcodes(TestCase): 
    
    def pre_auth(self):
        pass

    def test_base_request_with_tag(self): 
        response = requests.get(URL)
        self.assertEqual(response.status_code, 200)


    def test_no_city_returns_empty_str(self): 
        sample    = set_example(name="no-city")
        response  = requests.post(f"{URL}/zipcode-neighborhoods", json=sample["input"])
        nbhd_dict = response.json().get("neighborhoods").get("neighborhoodsSet")[0]
        self.assertNotIn("city", nbhd_dict)
        

    def test_example_is_successful(self):
        sample   = set_example()
        response = requests.post(f"{URL}/zipcode-neighborhoods", json=sample["input"])
        self.assertEqual(response.status_code, 200)


    def test_no_zipcodes_returns_404(self): 
        sample   = set_example(name="no-nbhd")
        response = requests.post(f"{URL}/zipcode-neighborhoods", json=sample["input"])
        self.assertEqual(response.status_code, 404)



if __name__ == "__main__": 
    import sys
    import config
    
    ENV = config.DEFAULT_ENV if len(sys.argv) == 1 else sys.argv.pop()
    URL = config.ENV_URLS.get(ENV)

    unit_main()

if False:
    import requests
    from importlib import reload
    from tests import test_zipcodes
    import config

    ENV = "local" # "staging" # "qa" # "local" # "qa" # "staging" # 
    URL = config.ENV_URLS[ENV]
    
    reload(config)
    reload(test_zipcodes)
    
    setup_json = set_example("no-city")
    an_input   = setup_json["input"]
    a_request  = an_input["neighborhoodsRequest"]
    
    a_response = requests.post(f"{URL}/zipcode-neighborhoods", json=an_input)
    a_response.status_code
    print(a_response.text)


    b_response = requests.get(URL)

    