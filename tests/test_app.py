
from fastapi.testclient import TestClient

from src.app.start import app
from src.app import models  # %s/[bz]_models/models/g

# from src.app.main import app
# from src.app.banks import models as b_models
# from src.app.zipcodes import models as z_models

client = TestClient(app)


class TestBanks:
    def test_root_call_responds_200(self): 
        response = client.get('/')
        assert response.status_code == 200, "Root call isn't successful."

    def test_all_banks_responds_200(self): 
        response = client.get('/national-banks')
        assert response.status_code == 200, "All banks not available."

    def test_valid_clabe_responds_200(self, clabe_valid): 
        response = client.get(f'/national-banks/parse-clabe/{clabe_valid}')
        assert response.status_code == 200, "Valid CLABE not successful."

    def test_invalid_clabe_responds_404(self, clabe_invalid):
        response = client.get(f'/national-banks/parse-clabe/{clabe_invalid}')
        assert response.status_code == 404, "Invalid CLABE not 404-ing."

    def test_plain_card_number_responds_card_bin_object(self, card_number): 
        response = client.get(f'/national-banks/card-number/{card_number}')
        assert response.status_code == 200,\
            f"Calling card-number (bin) on '{card_number}' doesn't return 200."
        resp_bin = models.CardsBin.parse_obj(response.json())
        assert isinstance(resp_bin, models.CardsBin),\
            f"Calling card-number (bin) on '{card_number}' doesn't give a valid bin."
                
    def test_card_number_with_bank_header_responds_bank_object(self, card_number): 
        accept_headers = {'Accept': 'application/bankobject+json'}
        url_with_number = f'/national-banks/card-number/{card_number}'
        response = client.get(url_with_number, headers=accept_headers)
        assert response.status_code == 200,\
            "Calling Card number with 'bankobject' header doesn't return 200."
        resp_bank = models.Bank.parse_obj(response.json())
        assert isinstance(resp_bank, models.Bank),\
            "Calling Card number with 'bankobject' header doesn't return bank object."
        

class TestZipcodes: 
    def test_zipcode_sin_ciudad_responds_empty_str(self, zipcode_sin_ciudad): 
        response = client.get(f'/zipcode-neighborhoods/{zipcode_sin_ciudad}')
        parsed = models.NeighborhoodsResponse.parse_obj(response.json()) 
        first_city = parsed.neighborhoods.neighborhoodsSet[0].city
        assert first_city == "",\
            f"no-city zipcode {zipcode_sin_ciudad} doesn't return empty string."
    
    def test_zipcode_ok_responds_ok(self, zipcode_ok): 
        response = client.get(f'/zipcode-neighborhoods/{zipcode_ok}')
        assert response.status_code == 200,\
            f"OK zipcode {zipcode_ok} isn't successful."
    
    def test_zipcode_sin_colonia_responds_404(self, zipcode_sin_colonia): 
        response = client.get(f'/zipcode-neighborhoods/{zipcode_sin_colonia}')
        assert response.status_code == 404,\
            f"sin-colonia zipcode {zipcode_sin_colonia} didn't 404'd."

    def skip_test_post_request_zipcode_responds_200(self, zipcode_ok): 
        req_1 = models.NeighborhoodsRequest(zipcode=zipcode_ok)
        req_2 = models.MetaRequestNbhd(neighborhoodsRequest=req_1)
        response = client.post('/zipcode-neighborhoods', data=req_2)
        assert response.status_code == 200,\
            "Este test dejó de servir y no se puede componer, lo bueno es que es de legacy"

