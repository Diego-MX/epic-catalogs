
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.app.start import app
from src.app import models

client = TestClient(app)

class TestBanks: 
    @classmethod
    def setup_class(cls): 
        cls.valid_clabe = '002180700845152894'
        cls.invalid_clabe = '002180700845282896'
        cls.card_number = '5499490544796915'

    def test_root_call_is_successful(self): 
        response = client.get('/')
        assert response.status_code == 200, "Root call isn't successful."

    def test_all_banks_is_successful(self): 
        response = client.get('/national-banks')
        assert response.status_code==200, "All banks not available."

    def test_valid_clabe_is_successful(self): 
        valid_one = self.valid_clabe
        response = client.get(f'/national-banks/parse-clabe/{valid_one}')
        assert response.status_code == 200, "Valid CLABE not successful."

    def test_invalid_clabe_returns_404(self):
        invalid_one = self.invalid_clabe
        response = client.get(f'/national-banks/parse-clabe/{invalid_one}')
        assert response.status_code == 404, "Invalid CLABE not successful."

    def test_card_number_is_successful(self): 
        a_card = self.card_number
        response = client.get(f'/national-banks/card-number/{a_card}')
        institucion = response.json()['bank']
        assert institucion == 'CITIBANAMEX', "Example card doesn't return Banamex."


class TestZipcodes: 
    @classmethod
    def setup_class(cls):
        cls.zipcodes = {
            'ok': 15530, 
            'no-city': 54200, 
            'sin-colonia': '01025'}

    def as_request(self, zipcode): 
        return models.NeighborhoodsRequest(zipcode=zipcode)


    def test_no_city_returns_empty_str(self): 
        a_zipcode = self.zipcodes['no-city']
        the_data = self.as_request(a_zipcode)
        response = client.post('/zipcode-nighborhoods', data=the_data)
        first_result = response.json()['neighborhoods']['neighborhoodsSet'][0]
        assert first_result["city"] == "", f"Zipcode {a_zipcode} doesn't return empty string."
    
    def test_specific_zipcode_returns_ok(self): 
        a_zipcode = self.zipcodes['ok']
        the_data = self.as_request(a_zipcode)
        response = client.post('/zipcode-neighborhoods', data=the_data)
        assert response.status_code == 200, f"Zipcode {a_zipcode} isn't successful."
    
    def test_example_is_successful(self):
        a_zipcode = self.zipcodes['ok']
        the_data = self.as_request(a_zipcode)
        response = client.post('/zipcode-neighborhoods', data=the_data)
        assert response.status_code == 200, f"Zipcode {a_zipcode} isn't successful."
    
    def test_no_zipcodes_returns_404(self): 
        a_zipcode = self.zipcodes['sin-colonia']
        the_data = self.as_request(a_zipcode)
        response = client.post('/zipcode-neighborhoods', data=the_data)
        assert response.status_code == 404, f"Zipcode sin colonia {a_zipcode} didn't 404'd."
    
    