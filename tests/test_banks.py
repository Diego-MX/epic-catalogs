
from unittest import TestCase, main as unit_main
import requests



class TestBanks(TestCase): 
    

    def test_bank_successful(self): 
        the_response = requests.get(f"{URL}/national-banks", json={})
        self.assertEqual(the_response.status_code, 200)

    

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

    ENV = "local" # "qa" # "qa" # "staging" # 
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

    