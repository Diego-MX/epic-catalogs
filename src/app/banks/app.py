
from typing import Union
from typing_extensions import Annotated
from fastapi import APIRouter, Header, Request

from src import tools
from . import engine, models



router = APIRouter(tags=['Banks'])

@router.get('', response_model=models.BanksResponse)
def list_all_banks(include_non_spei: bool=False): 
    the_banks = engine.all_banks(include_non_spei)
    banks_keys = {
        'numberOfRecords' : 'numberOfBanks',
        'attributes'      : 'bankAttributes',
        'recordSet'       : 'banksSet'}
    banks_resp = tools.dataframe_response(the_banks, None, banks_keys)
    banks_resp.pop('pagination')    
    return banks_resp


@router.get('/parse-clabe/{clabe_key}', response_model=models.Bank)
def get_bank_details_from_clabe(clabe_key: str): 
    return engine.clabe_parse(clabe_key)


@router.get('/card-number/{card_number}', 
        response_model=Union[models.CardsBin, models.Bank])
def get_bank_details_from_card_number(card_number: str, request: Request):
    #     accept: Annotated[str, Header()]=''):
    # bank_header = 'bankobject' in accept
    bank_header = 'bankobject' in request.headers.get('Accept', '')
    call_by = 'bank' if bank_header else 'bin'
    the_bin = engine.card_number_bin(card_number)
    return the_bin if call_by == 'bin' else engine.bin_bank(the_bin['banxicoId'])
    


@router.get('/acquiring/{acquire_code}', response_model=models.BankAcquiring)
def get_acquiring_bank_details(acquire_code: str): 
    return engine.bank_acquiring(acquire_code)

