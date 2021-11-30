
from unittest import TestCase, main as unit_main
import requests



class TestBanks(TestCase): 
    
    def test_bank_successful(self): 
        the_response = requests.get(f"{URL}/national-banks")
        self.assertEqual(the_response.status_code, 200)

    def test_clabe_successful(self): 
        clabe = "002180700845152894"
        response = requests.post(f"{URL}/national-banks/parse-clabe/{clabe}")
        self.assertEqual(response.status_code, 200)

    def test_card_number(self): 
        card_num = "5499490544796915"
        response = requests.post(f"{URL}/national-banks/card-number/{card_num}")
        institucion = response.json()["Institución"]
        self.assertEqual(institucion, "CITIBANAMEX")


if __name__ == "__main__": 
    import sys
    import config
    
    ENV = config.DEFAULT_ENV if len(sys.argv) == 1 else sys.argv.pop()
    URL = config.URLS.get(ENV)

    unit_main()

if False:
    from importlib import reload
    from tests import test_zipcodes
    import config

    ENV = "local-fastapi" # "local" # "qa" # "qa" # "staging" # 
    URL = config.URLS[ENV]
    
    reload(config)
    reload(test_zipcodes)
    
    setup_json = set_example("no-city")
    an_input   = setup_json["input"]
    a_request  = an_input["neighborhoodsRequest"]
    
    clabe = "002180700845152894"
    response = requests.post(f"{URL}/national-banks/parse-clabe/{clabe}")
    
    print(a_response.text)


    b_response = requests.get(URL)

    