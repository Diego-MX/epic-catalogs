
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.app.main import app
from src.app.banks import models as b_models
from src.app.zipcodes import models as z_models

client = TestClient(app)


class TestBanks:
    def response_model(self, response, model:BaseModel): 
        return model.parse_obj(response.json())

    def test_root_call_responds_200(self): 
        response = client.get('/')
        assert response.status_code == 200, "Root call isn't successful."

    def test_all_banks_responds_200(self): 
        response = client.get('/national-banks')
        assert response.status_code == 200, "All banks not available."

    def test_valid_clabe_responds_200(self, valid_clabe): 
        response = client.get(f'/national-banks/parse-clabe/{valid_clabe}')
        assert response.status_code == 200, "Valid CLABE not successful."

    def test_invalid_clabe_responds_404(self, invalid_clabe):
        response = client.get(f'/national-banks/parse-clabe/{invalid_clabe}')
        assert response.status_code == 404, "Invalid CLABE not 404-ing."

    def test_banamex_card_responds_banamex(self, banamex_card): 
        response = client.get(f'/national-banks/card-number/{banamex_card}')
        resp_model = self.response_model(response, b_models.CardsBin)
        assert resp_model.bank == 'CITIBANAMEX',\
            "Banamex card doesn't return Banamex."


class TestZipcodes: 
    def test_no_city_responds_empty_str(self, no_city_zipcode): 
        response = client.get(f'/zipcode-neighborhoods/{no_city_zipcode}')
        first_result = response.json()['neighborhoods']['neighborhoodsSet'][0]
        assert first_result["city"] == "",\
            f"no-city zipcode {no_city_zipcode} doesn't return empty string."
    
    def test_ok_zipcode_responds_ok(self, ok_zipcode): 
        response = client.get(f'/zipcode-neighborhoods/{ok_zipcode}')
        assert response.status_code == 200,\
            f"OK zipcode {ok_zipcode} isn't successful."
    
    def test_no_zipcodes_responds_404(self, no_colonia_zipcode): 
        response = client.get(f'/zipcode-neighborhoods/{no_colonia_zipcode}')
        assert response.status_code == 404,\
            f"sin-colonia zipcode {no_colonia_zipcode} didn't 404'd."
    

class SkipTestLegacyZipcodes: 
    def zipcode_meta_request(self, a_zipcode): 
        n_request = z_models.NeighborhoodsRequest(zipcode=a_zipcode)
        return z_models.MetaRequestNbhd(neighborhoodsRequest=n_request)  

    # def test_no_city_responds_empty_string(self, no_city_zipcode): 
    #     the_data = self.zipcode_meta_request(no_city_zipcode)
    #     response = client.post('/zipcode-neighborhoods', data=the_data)
    #     first_result = response.json()['neighborhoods']['neighborhoodsSet'][0]
    #     assert first_result["city"] == "",\
    #         f"no-city zipcode {no_city_zipcode} doesn't return empty string."
    
    def test_ok_zipcode_responds_ok(self, ok_zipcode): 
        the_data = self.zipcode_meta_request(ok_zipcode)
        response = client.post('/zipcode-neighborhoods', data=the_data)
        assert response.status_code == 200,\
            f"OK zipcode {ok_zipcode} isn't successful."
    
    def test_no_colonia_responds_404(self, no_colonia_zipcode): 
        the_data = self.zipcode_meta_request(no_colonia_zipcode)
        response = client.post('/zipcode-neighborhoods', data=the_data)
        assert response.status_code == 404,\
            f"sin-colonia zipcode {no_colonia_zipcode} didn't 404'd."
    
    