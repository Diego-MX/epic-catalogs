
"""
engine banks, contiene toda la información respecto a las 
peticiones a la base de datos.
"""
from inspect import currentframe
from pathlib import Path

import time
from sqlalchemy.orm import sessionmaker
import pandas as pd

import clabe
from src.app.exceptions import ValidationError, NotFoundError
from src import tools
from . import models

ctlg_dir = Path('refs/catalogs')

str_to_bool = lambda srs: (srs == 'True')


def queryrow_to_dict(a_df: pd.DataFrame, q: str, sword: str) -> dict:
    """
    Realiza un query en los datos de requeridos 
    """
    # caller_locals = currentframe().f_back.f_locals # D
    # q_df = a_df.query(q, local_dict=caller_locals) # D
    query_str = "`"+sword+"` == @change"
    q_df = a_df.query(query_str, local_dict={'change':q})
    assert q_df.shape[0] == 1, f"Query '{q}' doesn't return one row"
    return q_df.to_dict(orient='records')[0]

inicio=time.time()
engine = tools.get_connection()
banks_df = (pd.read_sql_table("national_banks",engine)
            .rename(columns={'banxico_id': 'banxicoId'})
            .assign(spei = lambda df: str_to_bool(df['spei']),
                    portability = lambda df: str_to_bool(df['portability']))
            .sort_values(by = "index"))
engine.dispose()
fin=time.time()
print(f"TE: {round(fin-inicio,2)} seg")

def all_banks(include_non_spei:bool) -> pd.DataFrame:
    """
    Extrae toda la información mediante el SPEI.
    """
    return banks_df.loc[banks_df['spei'], :] if include_non_spei else banks_df


def clabe_parse(clabe_key:str) -> models.Bank:
    """
    Obtención de la CLABE
    """
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
    bank_row = queryrow_to_dict(banks_df,q_code,"code")
    return models.Bank(**bank_row)


def card_number_bin(card_num:str) -> models.CardsBin:
    """
    Obtención de bins
    """
    inicio_bi=time.time()
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
    # engine=tools.get_connection()
    sesion = sessionmaker(bind=engine) # ORM
    session = sesion()
    resultado_national_banks_bin = session.query(models.NationalBanksBins).all()

    data_national_banks_bin=[{"bin":contenido.BIN, "length":contenido.Rango, "bankId":contenido.ID,
                          "banxicoId":contenido.banxico_id,"bank":getattr(contenido,"Institución"),
                          "nature":contenido.Naturaleza,
    "brand":contenido.Marca} for contenido in resultado_national_banks_bin]
    session.close()
    bins_df = pd.DataFrame(data_national_banks_bin)

    length_bins = bins_df.set_index('bin').groupby('length')
    for b_len, len_bins in length_bins.groups.items():
        bin_int = int(card_num[:b_len])
        if bin_int in len_bins:
            # bin_row = queryrow_to_dict(bins_df, f"`bin` == {bin_int}") # D
            bin_row = queryrow_to_dict(bins_df, bin_int,"bin")
            fin_bi = time.time()
            print(f"TE: {round(fin_bi-inicio_bi,2)} seg")
            return models.CardsBin(**bin_row)
            # Sin comillas porque INT.

    raise NotFoundError('Card bin not found',
        'Card bins correspond to the first [6,7,8] digits of the card number.')


def bin_bank(bank_key: str) -> models.Bank:
    """
    Se obtine la información del banco correspondiente
    """
    # bank_row = queryrow_to_dict(banks_df, f"`banxicoId` == '{bank_key}'") # D
    bank_row = queryrow_to_dict(banks_df, bank_key,"banxicoId")
    return models.Bank(**bank_row)


def bank_acquiring(acq_code: str) -> models.BankAcquiring:
    """
    Obtención de datos del acquiring banks
    """
    inicio_ac=time.time()

    # engine=tools.get_connection() # sí se coloca consume más tiempo
    sesion = sessionmaker(bind=engine) # ORM
    session = sesion()
    resultado_national_banks_acquiring = session.query(models.NationalBanksAcquiring).all()

    data_national_banks_acquiring=[{"tabla_id":contenido.tabla_id,
                                    "name":getattr(contenido, "Institución"),
                                    "codeAcquiring":getattr(contenido,"ID Adquirente"),
                                    "Cámara":getattr(contenido, "Cámara"),
        "Fecha de Alta":getattr(contenido,"Fecha de Alta")
        } for contenido in resultado_national_banks_acquiring]
    acq_banks = pd.DataFrame(data_national_banks_acquiring)
    session.close()

    # acq_row =queryrow_to_dict(acq_banks, f"`codeAcquiring` == '{acq_code}'") # D
    acq_row=queryrow_to_dict(acq_banks,acq_code,"codeAcquiring")
    fin_ac=time.time()
    print(f"TE: {round(fin_ac-inicio_ac,2)} seg")
    return models.BankAcquiring(**acq_row)
