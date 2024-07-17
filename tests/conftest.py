from pytest import fixture

## Banks
@fixture()
def valid_clabe(): 
    return '002180700845152894'

@fixture()
def invalid_clabe(): 
    return '002180700845282896'

@fixture()
def card_number(): 
    return '5499490544796915'

@fixture()
def banamex_card(): 
    return '5499490544796915'


## ZipCodes 
@fixture()
def ok_zipcode():
    return 15530

@fixture()
def no_city_zipcode():
    return 54200

@fixture()
def no_colonia_zipcode():
    return '01025'
