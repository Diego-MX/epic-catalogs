
from warnings import warn

from fastapi.testclient import TestClient
from httpx import Client
from pytest import fixture

from src.app.main import app

## Setup
def pytest_addoption(parser):
    parser.addoption('--client', action='store', default='testclient',
        help="Server URL against which to run the tests.")

@fixture(scope='session')
def client(request): 
    client_opt = request.config.getoption('--client')
    if client_opt == 'testclient':
        return TestClient(app)
    if client_opt == 'localhost': 
        return Client(base_url='http://localhost:80')
    warn(f"Using --client '{client_opt}' as a URL server.")
    return Client(base_url=client_opt)


## Banks
@fixture()
def clabe_valid(): 
    return '002180700845152894'

@fixture()
def clabe_invalid(): 
    return '002180700845282896'

@fixture()
def card_num(): 
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
