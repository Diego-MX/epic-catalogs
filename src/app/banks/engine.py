
from inspect import currentframe
from pathlib import Path

import pandas as pd

import clabe
from src.app.exceptions import ValidationError, NotFoundError
from . import models
from src import tools

ctlg_dir = Path('refs/catalogs')

str_to_bool = lambda srs: (srs == 'True')


def queryrow_to_dict(a_df: pd.DataFrame, q: str) -> dict: 
    caller_locals = currentframe().f_back.f_locals    
    q_df = a_df.query(q, local_dict=caller_locals)
    assert q_df.shape[0] == 1, f"Query '{q}' doesn't return one row"
    return q_df.to_dict(orient='records')[0]

engine = tools.get_connection()
banks_df = (pd.read_sql_table("national_banks",engine)
            .rename(columns={'banxico_id': 'banxicoId'})
            .assign(spei = lambda df: str_to_bool(df['spei']),
                    portability = lambda df: str_to_bool(df['portability']))
            .sort_values(by = "tabla_id"))
engine.dispose()

def all_banks(include_non_spei:bool) -> pd.DataFrame:
    return banks_df.loc[banks_df['spei'], :] if include_non_spei else banks_df


def clabe_parse(clabe_key:str) -> models.Bank:
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
    bank_row = queryrow_to_dict(banks_df, f"`code` == '{q_code}'")
    return models.Bank(**bank_row)


def card_number_bin(card_num:str) -> models.CardsBin:
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

    query_bins = """
            SELECT BIN AS bin,
                Rango AS "length",
                ID AS bankId,
                banxico_id AS banxicoId,
                Institución AS bank,
                Naturaleza AS nature,
                Marca AS brand
            FROM national_banks_bins;
                """
    
    engine_card = tools.get_connection()
    bins_df = pd.read_sql_query(query_bins,engine_card)
    engine_card.dispose()

    length_bins = bins_df.set_index('bin').groupby('length') 
    for b_len, len_bins in length_bins.groups.items(): 
        bin_int = int(card_num[:b_len])
        if bin_int in len_bins: 
            bin_row = queryrow_to_dict(bins_df, f"`bin` == {bin_int}")
            return models.CardsBin(**bin_row)
            # Sin comillas porque INT. 

    raise NotFoundError('Card bin not found', 
        'Card bins correspond to the first [6,7,8] digits of the card number.')


def bin_bank(bank_key: str) -> models.Bank: 
    bank_row = queryrow_to_dict(banks_df, f"`banxicoId` == '{bank_key}'")
    return models.Bank(**bank_row)


def bank_acquiring(acq_code: str) -> models.BankAcquiring: 
    query_acquiring = """
                    SELECT tabla_id,
                        "Institución" AS "name", 
                        "ID Adquirente" AS "codeAcquiring", 
                        Cámara, [Fecha de Alta]
                    FROM national_banks_acquiring;
                    """

    engine_acquiring = tools.get_connection()
    acq_banks = pd.read_sql_query(query_acquiring,engine_acquiring)
    engine_acquiring.dispose()

    acq_row =queryrow_to_dict(acq_banks, f"`codeAcquiring` == '{acq_code}'")
    return models.BankAcquiring(**acq_row)    
