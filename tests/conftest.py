from pytest import fixture

## Banks
@fixture()
def clabe_valid(): 
    return '002180700845152894'

@fixture()
def clabe_invalid(): 
    return '002180700845282896'

@fixture()
def card_number(): 
    return '5499490544796915'



## ZipCodes 
@fixture()
def zipcode_ok():
    return 15530

@fixture()
def zipcode_sin_ciudad():
    return 54200

@fixture()
def zipcode_sin_colonia():
    return '01025'
