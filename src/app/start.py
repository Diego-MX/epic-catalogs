from json import loads
import sys
from typing import Union

from fastapi import FastAPI, Request
import uvicorn

from src.app import models
from src import engine
from config import VERSION


debug_mode = 'debug' in sys.argv
root_path = 'data/docs/v1/catalogs' if not debug_mode else None

app = FastAPI(title='Centralized catalogs.', version=VERSION, 
    description='Setup and query all-purpose catalogs.',
    openapi_tags=[
        {'name': 'Zipcodes'},
        {'name': 'Banks'}, 
        {'name': 'Base', 'description': 'Verify base call and version.'},
        {'name': 'Legacy'}],
    root_path=root_path,
    default_response_class=models.ORJSONResponse)
    

@app.get('/', tags=['Base'])
async def verify_base_endpoint():
    return {'App Running Version': VERSION}


@app.post('/zipcode-neighborhoods', tags=['Legacy'], 
        response_model=models.NeighborhoodsResponse)
async def post_zipcode_object(a_request: models.MetaRequestNbhd):
    an_input = loads(a_request.json())['neighborhoodsRequest']
    return engine.zipcode_request(an_input)


@app.get('/zipcode-neighborhoods', tags=['Legacy'], 
        response_model=models.NeighborhoodsResponse)
async def get_zipcode_object(a_request: models.MetaRequestNbhd):
    an_input = loads(a_request.json())['neighborhoodsRequest']
    b_response = engine.zipcode_request(an_input)
    return b_response


@app.get('/zipcode-neighborhoods/{zipcode}', tags=['Zipcodes'], 
        response_model=models.NeighborhoodsResponse)
async def preferred_zipcode_neighborhoods(zipcode: str):
    return engine.zipcode_request({'zipcode': zipcode})


@app.get('/national-banks', tags=['Banks'], 
        response_model=models.BanksResponse)
def list_all_banks(include_non_spei: bool=False): 
    return engine.banks_request(include_non_spei)


@app.get('/national-banks/parse-clabe/{clabe_key}', tags=['Banks'], 
        response_model=models.Bank)
def get_bank_details_from_clabe(clabe_key: str): 
    return engine.clabe_parse(clabe_key)


@app.get('/national-banks/card-number/{card_number}', tags=['Banks'], 
        response_model=Union[models.CardsBin, models.Bank])
def get_bank_details_from_card_number(card_number:str, request:Request): 
    if "application/bankobject+json" in request.headers.get("Accept", ""):
        bin_bank = engine.card_number_parse(card_number, 'bank')
    else: 
        bin_bank = engine.card_number_parse(card_number, 'bin')
    return bin_bank


@app.get('/national-banks/acquiring/{acquire_code}', tags=['Banks'], 
        response_model=models.BankAcquiring)
def get_acquiring_bank_details(acquire_code: str): 
    acquirer = engine.bank_acquiring(acquire_code)
    return acquirer


if __name__ == '__main__':
    
    if debug_mode: 
        uvicorn.run('__main__:app', port=80, host='0.0.0.0', reload=True)
    else: 
        uvicorn.run(app, port=80, host='0.0.0.0')

