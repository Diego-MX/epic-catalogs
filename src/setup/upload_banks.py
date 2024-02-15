# Diego Villamil, EPIC
# CDMX, 1 de diciembre de 2021

import pandas as pd
from pandas import DataFrame as pd_DF
# pylint: disable=redefined-outer-name


# Read:  api-catalogs.xlsx!(tabla_297|plazas_w|anexo_1,anexo_1c)
# Write: national-banks(-plazas|-bins)?

def process_banks(tbl_297:pd_DF): 
    dict_colnames = {
        'NOMBRE'      : 'name',
        'CLAVE'       : 'code',
        'BANCO'       : 'banxico_id',
        'nombre_corto': 'alias',
        'SPEI'        : 'spei', 
        'portabilidad': 'portability', 
        }    
        # 'PARAMETRO Activo / Desactivo': 'is_active', 
        #  'ordenante'   : 'ordenante'
        # 'Tipo banco' : 'type'}
    bank_df = (tbl_297 
        .rename(columns=dict_colnames)
        .loc[:, dict_colnames.values()]
        .assign(portability=lambda df: df['portability'] != -1)
        .astype(str))
    return bank_df


def process_plazas(tbl_plz:pd_DF): 
    dict_colnames = {
        'Nombre' : 'name',
        'Plaza'  : 'code'}

    ctlg_df = (tbl_plz
        .rename(columns=dict_colnames)
        .assign(code=lambda df: df.code.map(str).str.pad(3, fillchar='0')))
    return ctlg_df


def process_bins(bins_df:pd_DF, bins_1c:pd_DF, bins_cols:pd_DF):
    the_types = {'integer': int, 'character': str, 'date': 'datetime64[ns]'}
    bins_rename = { row['Ref Nombre']: the_types[row['Tipo']]
            for _, row in bins_cols.iterrows() if row['Tipo'] }

    bins_2c = (bins_1c[bins_rename.keys()]
        .astype(bins_rename))
    
    bins_1 = (bins_df
        .loc[:, bins_rename.keys()]
        .astype(bins_rename)
        .set_index('BIN'))

    bins_1.update(bins_2c)

    bins = (bins_1
        .assign(ID=lambda df: df['Id Institución'].astype(str).str[3:]))
    return bins


def process_adquirentes(tbl_29:pd_DF, acq_cols:pd_DF):
    df_types = {'int': int, 'str': str, 'date': 'datetime64[ns]'}
    acq_rename   = {row.nombre: df_types[row.type] 
            for _, row in acq_cols.iterrows() if row.type}

    acq_tbl  = (tbl_29
        .loc[:, acq_rename.keys()]
        .astype(acq_rename)
        .replace({'ID Adquirente': 0}, pd.NA))
    return acq_tbl



if __name__ == '__main__': 
    from dotenv import load_dotenv
    load_dotenv(override=True)

    from src.resources import AzureResourcer
    from src.tools import read_excel_table
    from config import SITE, ENV, SERVER


    local_path = SITE/'refs/catalogs'
    storage_path = 'product/epic-catalogs/app-services'    # pylint: disable=invalid-name 

    ctlg_files = {
        'banks'    : 'national-banks',
        'plazas'   : 'national-banks-plazas',
        'bins'     : 'national-banks-bins', 
        'acquiring': 'national-banks-acquiring'}
    
    base_excel = local_path/'api-catalogs.xlsx.lnk'

    banks_pre = read_excel_table(base_excel, 'banks', 'tabla_297')
    banks_df  = process_banks(banks_pre).reset_index().astype(str)
    banks_df.to_feather(local_path/f"{ctlg_files['banks']}.feather")
    
    plaza_pre = read_excel_table(base_excel, 'banks', 'plazas_w')
    plaza_df  = process_plazas(plaza_pre).reset_index()
    plaza_df.to_feather(local_path/f"{ctlg_files['plazas']}.feather")

    bins_cols = read_excel_table(base_excel, 'banks-bins', 'cols_anexo1')
    bins_pre  = read_excel_table(base_excel, 'banks-bins', 'anexo_1')
    bins_1c   = read_excel_table(base_excel, 'banks-bins', 'anexo_1c')
    bins_df   = process_bins(bins_pre, bins_1c, bins_cols).reset_index()
    bins_df.to_feather(local_path/f'{ctlg_files["bins"]}.feather')

    acq_cols = read_excel_table(base_excel, 'banks-acquiring', 'cols_anexo_29')
    acq_pre  = read_excel_table(base_excel, 'banks-acquiring', 'anexo_29')
    acq_df   = process_adquirentes(acq_pre, acq_cols).reset_index()
    acq_df.to_feather(local_path/f"{ctlg_files['acquiring']}.feather")


    resourcer = AzureResourcer(ENV, SERVER)
    blob_container = resourcer.get_blob_service()

    for each_file in ctlg_files.values(): 
        local_p  = local_path/f'{each_file}.feather'
        stg_path = f'{storage_path}/{each_file}.feather'

        the_blob = blob_container.get_blob_client(container='bronze', blob=stg_path)
        with open(local_p, 'rb') as _f: 
            the_blob.upload_blob(_f, overwrite=True)
