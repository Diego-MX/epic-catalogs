
from typing import Union
from fastapi import APIRouter, Request
from . import engine, models


router = APIRouter(prefix='/national-banks', tags=['Banks'])

@router.get('', response_model=models.BanksResponse)
def list_all_banks(include_non_spei: bool=False): 
    return engine.banks_request(include_non_spei)


@router.get('/parse-clabe/{clabe_key}', response_model=models.Bank)
def get_bank_details_from_clabe(clabe_key: str): 
    return engine.clabe_parse(clabe_key)


@router.get('/card-number/{card_number}', 
        response_model=Union[models.CardsBin, models.Bank])
def get_bank_details_from_card_number(card_number:str, request:Request): 
    bank_header = "application/bankobject+json" in request.headers.get('Accept', '')
    call_by = ('bank' if bank_header else 'bin')
    return engine.card_number_parse(card_number, call_by)


@router.get('/acquiring/{acquire_code}', response_model=models.BankAcquiring)
def get_acquiring_bank_details(acquire_code: str): 
    return engine.bank_acquiring(acquire_code)

