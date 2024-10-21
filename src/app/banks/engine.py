
"""
engine banks, contiene toda la información respecto a las 
peticiones a la base de datos.
"""
from pathlib import Path
from typing import Any

from sqlalchemy.orm import sessionmaker
import pandas as pd

import clabe

import src
from src.app.exceptions import ValidationError, NotFoundError
from src import tools

from . import models

WITH_SQL = (src.DATA_CONN != 'repo')

ctlg_dir = Path('refs/catalogs')
str_to_bool = lambda srs: (srs == 'True')
timer = tools.Timer(print_mode=WITH_SQL*-1)

if WITH_SQL:
    engine = src.tools.get_connection()
    pre_banks = pd.read_sql_table("national_banks", engine)
    engine.dispose()
    timer.set_mark("Load Base Banks")
else:
    pre_banks = pd.read_feather(ctlg_dir/"national-banks.feather")

banks_df = (pre_banks
    .rename(columns={'banxico_id': 'banxicoId'})
    .assign(spei = lambda df: str_to_bool(df['spei']),
        portability = lambda df: str_to_bool(df['portability']))
    .sort_values(by = "index"))


def _queryrow_to_dict(a_df: pd.DataFrame, column: str, value: Any) -> dict:
    """Realiza un query en los datos de requeridos"""
    # caller_locals = currentframe().f_back.f_locals # D
    # q_df = a_df.query(q, local_dict=caller_locals) # D
    one_row = (a_df[column] == value)
    assert len(one_row) == 1, f"Column '{column}' doesnt have one {value}."
    return a_df.loc[one_row, :].to_dict(orient='records')[0]
    

def all_banks(include_non_spei:bool=False) -> models.BanksResponse:
    """Extrae toda la información mediante el SPEI."""
    all_df = (banks_df if not include_non_spei
        else banks_df.loc[banks_df['spei'], :])
    return models.BanksResponse.from_df(all_df)


def clabe_parse(clabe_key:str) -> models.Bank:
    """Obtención de la CLABE"""
    verificator = clabe.compute_control_digit(clabe_key[:-1])
    if (clabe_key[-1] != verificator):
        raise ValidationError('Invalid CLABE',
            'CLABE is not valid, possibly due to its control digit.')

    gfb_code = '072'
    bineo_code = '165'

    bank_code = clabe_key[0:3]
    es_indirecto = clabe_key[3:5] == '99'
    gfb_a_bineo = clabe_key[7:9] == '20'

    is_bineo = (bank_code == gfb_code) and es_indirecto and gfb_a_bineo  
    q_code = bineo_code if is_bineo else bank_code
    bank_row = _queryrow_to_dict(banks_df, "code", q_code)
    return models.Bank.from_orm(bank_row)


def card_number_bin(card_num:str) -> models.CardsBin:
    """Obtención de bins"""
    
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
        'BIN'           : 'bin',
        'Rango'         : 'length',
        'ID'            : 'bankId',
        'banxico_id'    : 'banxicoId',
        'Institución'   : 'bank',
        'Naturaleza'    : 'nature',
        'Marca'         : 'brand'}
    bins_df = (pd.read_feather(ctlg_dir/'national-banks-bins.feather')
        .rename(columns=bin_cols)
        .loc[:, bin_cols.values()])

    length_bins = bins_df.set_index('bin').groupby('length')
    for b_len, len_bins in length_bins.groups.items():
        bin_int = int(card_num[:b_len])
        if bin_int in len_bins:
            # bin_row = _queryrow_to_dict(bins_df, f"`bin` == {bin_int}") # D
            bin_row = _queryrow_to_dict(bins_df, bin_int,"bin")
            timer.set_mark("Query Bin")
            return models.CardsBin(**bin_row)

    raise NotFoundError('Card bin not found', 
        'Card bins correspond to the first [6,7,8,9] digits of the card number.')


def bin_bank(bank_key: str) -> models.Bank:
    """Se obtine la información del banco correspondiente"""
    # bank_row = _queryrow_to_dict(banks_df, f"`banxicoId` == '{bank_key}'") # D
    bank_row = _queryrow_to_dict(banks_df, "banxicoId", bank_key)
    return models.Bank.from_orm(bank_row)


def bank_acquiring(acq_code: str) -> models.BankAcquiring:
    """Obtención de datos del acquiring banks"""
    if WITH_SQL: 
        sesion = sessionmaker(bind=engine) # ORM
        session = sesion()
        resultado_national_banks_acquiring = session.query(models.NationalBanksAcquiring).all()
        acq_attrs = {
            'tabla_id'      : 'tabla_id', 
            'Institución'   : 'name', 
            'ID Adquirente' : 'codeAcquiring', 
            'Cámara'        : 'Cámara', 
            'Fecha de Alta' : 'Fecha de Alta'}
        data_national_banks_acquiring=[
            {k: getattr(contenido, v) for k, v in acq_attrs.items()}
            for contenido in resultado_national_banks_acquiring]
        acq_banks = pd.DataFrame(data_national_banks_acquiring)
        session.close()
        timer.set_mark("Query Acquiring")   
    else: 
        acq_cols = {
            'Institución' : 'name', 
            'ID Adquirente' : 'codeAcquiring'}
        acq_banks = (pd.read_feather(ctlg_dir/'national-banks-acquiring.feather')
            .rename(columns=acq_cols))
    
    acq_row = _queryrow_to_dict(acq_banks, "codeAcquiring", acq_code)
    return models.BankAcquiring(**acq_row)
