
from pathlib import Path

from collections import defaultdict
from json import loads

import pandas as pd

import clabe
from src.app.exceptions import ValidationError, NotFoundError
from src import tools

ctlg_dir = Path('refs/catalogs')

str_to_bool = lambda srs: (srs == 'True')

banks_df = (pd.read_feather(ctlg_dir/'national-banks.feather')
    .rename(columns={'banxico_id': 'banxicoId'})
    .assign(spei = lambda df: str_to_bool(df['spei']), 
        portability = lambda df: str_to_bool(df['portability'])))


def banks_request(include_non_spei):
    resp_df = banks_df[banks_df['spei']] if include_non_spei else banks_df
    banks_keys = {
        'numberOfRecords' : 'numberOfBanks',
        'attributes'      : 'bankAttributes',
        'recordSet'       : 'banksSet'}
    banks_resp = tools.dataframe_response(resp_df, None, banks_keys)
    banks_resp.pop('pagination')
    return banks_resp


def clabe_parse(clabe_key):
    gfb_code = '072'
    bineo_code = '165'
    
    bank_code = clabe_key[0:3]
    es_indirecto = clabe_key[3:5] == '99'
    gfb_a_bineo = clabe_key[7:9] == '20'

    verificator = clabe.compute_control_digit(clabe_key[:-1])
    if (clabe_key[-1] != verificator):
        raise ValidationError('Invalid CLABE', 
            'CLABE is not valid, possibly due to its control digit.')

    bank_code = clabe_key[0:3]
    in_banks = (bank_code == banks_df.code)

    if in_banks.sum() != 1:
        raise NotFoundError('Non unique bank', 
            'Bank is not registered or unique.')       

    el_banco = banks_df.loc[in_banks, :]
    
    if (bank_code == gfb_code) and es_indirecto and gfb_a_bineo: 
        el_banco = banks_df.loc[banks_df.code == bineo_code]     
    
    return el_banco.to_dict(orient='records')[0]



def card_number_parse(card_num, response_obj='bin'):
    if len(card_num) != 16:
        raise ValidationError('Invalid card number', 
            'Card Number must have 16 digits.')

    # ['Longitud', 'Id Institución', 'Institución', 'Naturaleza', 'Marca',
    # 'Tarjeta Chip', 'BIN Virtual', 'Ac Manual', 'Ac TPV',
    # 'Ac Cashback', 'Ac ATMs', 'Ac Ecommerce', 'Ac Cargos Periódicos',
    # 'Ac Ventas X Teléfono', 'Ac Sucursal', 'Ac Pagos en el Intercambio',
    # 'Ac 3D Secure', 'NFC', 'MST', 'Wallet', 'PAN Din', 'CVV/CVC Din',
    # 'NIP', 'Tokenización', 'Vale', 'Fecha de Alta', 'Procesador']
    # ... ID calculada.
    bin_cols = {
        'Rango'         : 'length',
        'ID'            : 'bankId',
        'banxico_id'    : 'banxicoId',
        'Institución'   : 'bank',
        'Naturaleza'    : 'nature',
        'Marca'         : 'brand'}

    bins_df = (pd.read_feather(ctlg_dir/'national-banks-bins.feather')
        .set_index('BIN')
        .rename(columns=bin_cols)
        .loc[:, bin_cols.values()])
    
    bin_lengths = defaultdict(list)
    for a_bin, length in bins_df['length'].items():
        bin_lengths[length].append(a_bin)

    try_bin = False
    for length in sorted(bin_lengths.keys(), reverse=True):
        try_bin = int(card_num[:length]) in bin_lengths[length]
        if try_bin:
            bin_int = int(card_num[:length])
            the_bin = bins_df.loc[bin_int, :]

            if response_obj == 'bin': 
                pre_response = loads(the_bin.to_json())
                pre_response['bin'] = str(the_bin.name)
            
            elif response_obj == 'bank': 
                its_bank = banks_df.set_index('banxicoId').loc[the_bin.banxicoId]
                pre_response = loads(its_bank.to_json())
                pre_response['banxicoId'] = the_bin.banxicoId
                pre_response.pop('index')

            return pre_response
    raise NotFoundError('Card bin not found', 
        'Card bins correspond to the first [6,7,8] digits of the card number.')


def bank_acquiring(acquiring_code): 
    acq_cols = {
        'Institución' : 'name', 
        'ID Adquirente' : 'codeAcquiring'}
    acquiring_banks = (pd.read_feather(ctlg_dir/'national-banks-acquiring.feather')
        .rename(columns=acq_cols))

    find_any = (acquiring_banks['codeAcquiring'] == acquiring_code)
    
    if find_any.sum() != 1: 
        raise NotFoundError('Acquiring bank not found', 
            detail='Acquiring Bank is not registered or unique.')            

    return acquiring_banks[find_any].to_dict(orient='records')[0]

