# Engine es el back office de la aplicación.  
# test_engine prueba las funciones correspondientes. 

import pandas as pd
from pytest import raises

from src.app import exceptions
from src.app.banks import engine as b_engine, models as b_models
from src.app.zipcodes import engine as z_engine


class TestBanks:
    # banks_request (spei/no-spei)
    # clabe_parse
    # card_number_bin
    # acquiring   

    def test_all_banks_is_dataframe(self): 
        them_all = b_engine.all_banks(False)
        assert isinstance(them_all, pd.DataFrame),\
            "All-Banks-Engine falla con el Dataframe."

    def test_valid_clabe_returns_bank(self, valid_clabe): 
        clabe_bank = b_engine.clabe_parse(valid_clabe)
        assert isinstance(clabe_bank, b_models.Bank),\
            f"La CLABE válida {valid_clabe} falla con el modelo Bank."

    def test_invalid_clabe_raises_validation_error(self, invalid_clabe):
        with raises(exceptions.ValidationError) as excinfo: 
            b_engine.clabe_parse(invalid_clabe)
        assert excinfo.type is exceptions.ValidationError,\
            f"La clabe inválida '{invalid_clabe}' falla en el error de validación."

    def text_bineo_transfer_returns_bineo(self, bineo_clabe): 
        clabe_bank = b_engine.clabe_parse(bineo_clabe)
        assert clabe_bank.name == 'Bineo',\
            f"La Clabe de Bineo {bineo_clabe} falla con el banco Bineo."

    def test_card_number_returns_bin(self, card_num): 
        the_bin = b_engine.card_number_bin(card_num)
        assert isinstance(the_bin, b_models.CardsBin),\
            f"Engine de Card Number para '{card_num}' falla con el modelo Bin."


class SkipTestZipcodes: 
    # zipcode_(request|query|response|warnings)

    def test_no_city_zipcode_to_emtpy_city(self, no_city_zipcode): 
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
    
    