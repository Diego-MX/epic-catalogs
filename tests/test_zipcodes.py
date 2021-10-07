from unittest import TestCase, main as unit_main
from datetime import datetime as dt 
import requests


URL = "http://localhost:5000/v1/catalogs/get-zipcode-neighborhoods"
# URL = "https://wap-cx-collections-dev.azurewebsites.net/v1/catalogs/get-zipcode-neighborhoods"


class TestLoanMessages(TestCase): 
    def set_example(self):
        example_request = { 
            "input"     : {
                "neighborhoodsRequest": {
                    "zipcode": "92773"}, 
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


    def test_simple_request_is_successful(self):
        sample   = self.set_example()
        response = requests.post(URL, json=sample["input"])
        self.assertEqual(response.status_code, 200)


    def test_app_matches_filter_to_catalog(self):
        pass 

    def test_app_breaks_about_unmatched_filter_in_catalog(self): 
        pass 


if __name__ == "__main__": 
    unit_main()

else: 
    from tests import test_app 
    
    from importlib import reload
    reload(test_app)

    some_test = test_app.TestFilters()
    simple = some_test.simple_example()
    an_input = simple["input"]
    a_request = an_input["collectionsMessagesRequest"]
    
    a_response = requests.post(URL, json=an_input)

    a_response.status_code
    print(a_response.text)
    

    