# Diego Villamil, EPIC
# CDMX, 1 de diciembre de 2021
"""Read local Excel file, convert to Feather, and Upload to Blob.
"""
# pylint: disable=invalid-name 
# pylint: disable=redefined-outer-name
import pandas as pd

from src.tools import read_excel_table, Timer


def process_banks(el_excel:pd.DataFrame): 
    dict_colnames = {
        'NOMBRE'      : 'name',
        'CLAVE'       : 'code',
        'BANCO'       : 'banxico_id',
        'nombre_corto': 'alias',
        'SPEI'        : 'spei', 
        'portabilidad': 'portability'}    

    la_297 = read_excel_table(el_excel, 'banks', 'tabla_297')
    bank_df = (la_297
        .rename(columns=dict_colnames)
        .loc[:, dict_colnames.values()]
        .assign(portability=lambda df: df['portability'] != -1)
        .astype(str)
        .reset_index())
    return bank_df


def process_plazas(el_excel): 
    dict_colnames = {
        'Nombre' : 'name',
        'Plaza'  : 'code'}

    tbl_plz = read_excel_table(el_excel, 'banks', 'plazas_2')
    ctlg_df = (tbl_plz
        .rename(columns=dict_colnames)
        .assign(code=lambda df: df.code.map(str).str.pad(3, fillchar='0')))
    return ctlg_df


def process_bins(el_excel):
    bins_cols = read_excel_table(el_excel, 'banks-bins', 'cols_anexo1')
    
    the_types = {'integer': int, 'character': str, 
        'date': 'datetime64[ns]', 'bool': bool}

    bins_rename = { row['Ref Nombre']: the_types[row['Tipo']]
            for _, row in bins_cols.iterrows() if row['Tipo'] }

    bins = (read_excel_table(el_excel, 'banks-bins', 'anexo_1')
        .loc[:, bins_rename.keys()]
        .astype(bins_rename)
        .set_index('BIN')
        .assign(ID=lambda df: df['ID INSTITUCIÓN'].astype(str).str[3:])
        .reset_index())
    return bins


def process_adquirentes(el_excel):
    acq_cols = read_excel_table(el_excel, 'banks-acquiring', 'cols_anexo_29')
    df_types = {'int': int, 'str': str, 'date': 'datetime64[ns]'}
    acq_rename   = {row.nombre: df_types[row.type] 
            for _, row in acq_cols.iterrows() if row.type}

    acq_tbl  = (read_excel_table(el_excel, 'banks-acquiring', 'anexo_29')
        .loc[:, acq_rename.keys()]
        .astype(acq_rename)
        .replace({'ID Adquirente': 0}, pd.NA)
        .reset_index())
    return acq_tbl



if __name__ == '__main__': 
    from sys import argv

    from src.resources import AzureResourcer
    from src import SITE, ENV, SERVER

    no_blob = "no-blob" in argv
    time_it = "time-it" in argv
    my_timer = Timer(print_mode=not(time_it))

    local_path = SITE/'refs/catalogs'
    storage_path = 'product/epic-catalogs/app-services'    

    ctlg_files = {
        'banks'    : 'national-banks',
        'bins'     : 'national-banks-bins', 
        'acquiring': 'national-banks-acquiring'}
        # plazas: 'national-banks-plazas'
    
    base_excel = local_path/'api-catalogs.xlsx.lnk'
    

    banks_df  = process_banks(base_excel)
    banks_df.to_feather(local_path/f"{ctlg_files['banks']}.feather")
    my_timer.set_mark("Banks time")

    bins_df   = process_bins(base_excel)
    bins_df.to_feather(local_path/f'{ctlg_files["bins"]}.feather')
    my_timer.set_mark("Bins time")

    acq_df = process_adquirentes(base_excel)
    acq_df.to_feather(local_path/f"{ctlg_files['acquiring']}.feather")
    my_timer.set_mark("Acquiring time")

    if not no_blob: 
        resourcer = AzureResourcer(ENV, SERVER)
        blob_container = resourcer.get_blob_service()

        for each_file in ctlg_files.values(): 
            local_p  = local_path/f'{each_file}.feather'
            stg_path = f'{storage_path}/{each_file}.feather'

            the_blob = blob_container.get_blob_client(container='bronze', blob=stg_path)
            with open(local_p, 'rb') as _f: 
                the_blob.upload_blob(_f, overwrite=True)
