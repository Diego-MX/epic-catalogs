
from typing import Union
from typing_extensions import Annotated
from fastapi import APIRouter, Header

from . import engine, models


router = APIRouter()

@router.get('')
def list_all_banks(include_non_spei: bool=False) -> models.BanksResponse: 
    return engine.all_banks(include_non_spei)

@router.get('/parse-clabe/{clabe_key}')
def get_bank_details_from_clabe(clabe_key: str) -> models.Bank: 
    return engine.clabe_parse(clabe_key)

@router.get('/card-number/{card_number}')
def get_bank_details_from_card_number(card_number: str, 
        accept: Annotated[str, Header()]='') -> Union[models.CardsBin, models.Bank]:
    bank_header = 'bankobject' in accept
    call_by = 'bank' if bank_header else 'bin'
    the_bin = engine.card_number_bin(card_number)
    one_or_other = (the_bin if call_by == 'bin' 
        else engine.bin_bank(the_bin.banxicoId))
    return one_or_other
    

@router.get('/acquiring/{acquire_code}')
def get_acquiring_bank_details(acquire_code: str) -> models.BankAcquiring: 
    return engine.bank_acquiring(acquire_code)

