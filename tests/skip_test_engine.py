# Engine es el back office de la aplicación.  
# test_engine prueba las funciones correspondientes. 

from src.app.main import app as main_app
from src.app.banks import engine as bank_engine
from src.app.zipcodes import engine as zipcode_engine



class SkipTestBanks:
    # banks_request (spei/no-spei)
    # clabe_parse
    # card_number_parse
    # acquiring   

    def test_all_banks_response_200(self): 
        response = client.get('/national-banks')
        assert response.status_code == 200, "All banks not available."

    def test_valid_clabe_response_200(self, valid_clabe): 
        response = client.get(f'/national-banks/parse-clabe/{valid_clabe}')
        assert response.status_code == 200, "Valid CLABE not successful."

    def test_invalid_clabe_response_404(self, invalid_clabe):
        response = client.get(f'/national-banks/parse-clabe/{invalid_clabe}')
        assert response.status_code == 404, "Invalid CLABE not 404-ing."

    def test_banamex_card_responds_banamex(self, banamex_card): 
        response = client.get(f'/national-banks/card-number/{banamex_card}')
        institucion = response.json()['bank']
        assert institucion == 'CITIBANAMEX', "Banamex card doesn't return Banamex."


class SkipTestZipcodes: 
    # zipcode_(request|query|response|warnings)

    def test_no_city_response_empty_str(self, no_city_zipcode): 
        the_data = self.as_request(no_city_zipcode)
        response = client.post('/zipcode-nighborhoods', data=the_data)
        first_result = response.json()['neighborhoods']['neighborhoodsSet'][0]
        assert first_result["city"] == "",\
            f"no-city zipcode {no_city_zipcode} doesn't return empty string."
    
    def test_ok_zipcode_response_ok(self, ok_zipcode): 
        the_data = self.as_request(ok_zipcode)
        response = client.post('/zipcode-neighborhoods', data=the_data)
        assert response.status_code == 200,\
            f"OK zipcode {ok_zipcode} isn't successful."
    
    def test_no_zipcodes_response_404(self, no_colonia_zipcode): 
        the_data = self.as_request(no_colonia_zipcode)
        response = client.post('/zipcode-neighborhoods', data=the_data)
        assert response.status_code == 404,\
            f"sin-colonia zipcode {no_colonia_zipcode} didn't 404'd."
    
    