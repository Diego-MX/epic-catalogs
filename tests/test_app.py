
# pylint: disable=too-few-public-methods

from pytest import fixture

from src.app.banks import models as b_models
from src.app.zipcodes import models as z_models

class BaseTest: 
    client = None

    @fixture(autouse=True)
    def setup_client(self, client): 
        self.client = client


class TestMain(BaseTest):
    def test_root_call_responds_200(self): 
        response = self.client.get('/')
        assert response.status_code == 200, "El call raíz / falla en el 200."


class TestBanks(BaseTest):
    def test_all_banks_responds_200(self): 
        response = self.client.get('/national-banks')
        assert response.status_code == 200, "Call de All banks no está disponible."

    def test_valid_clabe_responds_200(self, clabe_valid): 
        response = self.client.get(f'/national-banks/parse-clabe/{clabe_valid}')
        assert response.status_code == 200,\
            f"La CLABE válida {clabe_valid} falla en responder 200."

    def test_invalid_clabe_responds_404(self, clabe_invalid):
        response = self.client.get(f'/national-banks/parse-clabe/{clabe_invalid}')
        assert response.status_code == 404,\
            f"La CLABE inválida {clabe_invalid} falla 404-ando."

    def test_plain_card_number_responds(self, card_num): 
        response = self.client.get(f'/national-banks/card-number/{card_num}')
        assert response.status_code == 200,\
            f"Calling card-number (bin) on '{card_num}' doesn't return 200."
        resp_bin = b_models.CardsBin.parse_obj(response.json())
        assert isinstance(resp_bin, b_models.CardsBin),\
            f"Calling card-number (bin) on '{card_num}' doesn't give a valid bin."
                
    def test_card_number_with_bank_header(self, card_num): 
        accept_headers = {'Accept': 'application/bankobject+json'}
        url_with_number = f'/national-banks/card-number/{card_num}'
        response = self.client.get(url_with_number, headers=accept_headers)
        assert response.status_code == 200,\
            "Calling Card number with 'bankobject' header doesn't return 200."
        resp_bank = b_models.Bank.parse_obj(response.json())
        assert isinstance(resp_bank, b_models.Bank),\
            "Calling Card number with 'bankobject' header doesn't return bank object."
        

class TestZipcodes(BaseTest): 
    def test_zipcode_sin_ciudad_responds_empty_str(self, zipcode_sin_ciudad): 
        response = self.client.get(f'/zipcode-neighborhoods/{zipcode_sin_ciudad}')
        parsed = z_models.NeighborhoodsResponse.parse_obj(response.json(), ) 
        first_city = parsed.neighborhoods.neighborhoodsSet[0].city
        assert first_city == "",\
            f"no-city zipcode {zipcode_sin_ciudad} doesn't return empty string."
    
    def test_zipcode_ok_responds_ok(self, zipcode_ok): 
        response = self.client.get(f'/zipcode-neighborhoods/{zipcode_ok}')
        assert response.status_code == 200,\
            f"OK zipcode {zipcode_ok} isn't successful."
    
    def test_zipcode_sin_colonia_responds_404(self, zipcode_sin_colonia): 
        response = self.client.get(f'/zipcode-neighborhoods/{zipcode_sin_colonia}')
        assert response.status_code == 404,\
            f"sin-colonia zipcode {zipcode_sin_colonia} didn't 404'd."

    def skip_test_post_request_zipcode_responds_200(self, zipcode_ok): 
        req_1 = z_models.NeighborhoodsRequest(zipcode=zipcode_ok)
        req_2 = z_models.MetaRequestNbhd(neighborhoodsRequest=req_1)
        response = self.client.post('/zipcode-neighborhoods', data=req_2)
        assert response.status_code == 200,\
            "Este test dejó de servir y no se puede componer, lo bueno es que es de legacy"

