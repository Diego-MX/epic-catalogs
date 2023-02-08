# Diego Villamil, EPIC
# CDMX, 1 de diciembre de 2021

# From Excel to Feather to Blob

# Read:  api-catalogs.xlsx!(tabla_297|plazas_w|anexo_1,anexo_1c)
# Write: national-banks(-plazas|-bins)?
from dotenv import load_dotenv
import pandas as pd

from src.resources import AzureResourcer
from src.tools import read_excel_table

load_dotenv(override=True)
from config import SITE, ENV, SERVER


#  General considerations
local_path = SITE/'refs/catalogs'

ctlg_files = {
    'banks'    : 'national-banks',
    'plazas'   : 'national-banks-plazas',
    'bins'     : 'national-banks-bins', 
    'acquiring': 'national-banks-acquiring'}

#  Banks

excel_call = (local_path/'api-catalogs.xlsx.lnk', 'banks', 'tabla_297')
dict_colnames = {
    'NOMBRE'      : 'name',
    'CLAVE'       : 'code',
    'BANCO'       : 'banxico_id',
    'nombre_corto': 'alias',
    'SPEI'        : 'spei'}
    # , 
    # 'PARAMETRO Activo / Desactivo': 'is_active', 
    # 'Tipo banco' : 'type'}

bank_df = (read_excel_table(*excel_call)
    .rename(columns=dict_colnames)
    .loc[:, dict_colnames.values()]
    .astype(str)
    .reset_index())

bank_df.to_feather(local_path/f"{ctlg_files['banks']}.feather")

# Las plazas son casi lo mismo. 

excel_call = (local_path/'api-catalogs.xlsx.lnk', 'banks', 'plazas_w')

dict_colnames = {
    'Nombre' : 'name',
    'Plaza'  : 'code'}

ctlg_df = (read_excel_table(*excel_call)
    .rename(columns=dict_colnames)
    .assign(code=lambda df: df.code.map(str).str.pad(3, fillchar='0')))

ctlg_df.to_feather(local_path/f'{ctlg_files["plazas"]}.feather')


# Los Bins sí requieren algo de manipulación. 

the_types = {'integer': int, 'character': str, 'date': 'datetime64[ns]'}

excel_call = (local_path/'api-catalogs.xlsx.lnk', 'banks-bins', 'cols_anexo1')
bins_cols_ = read_excel_table(*excel_call)
bins_cols = { row['Ref Nombre']: the_types[row['Tipo']]
        for _, row in bins_cols_.iterrows() if row['Tipo'] }

excel_call = (local_path/'api-catalogs.xlsx.lnk', 'banks-bins', 'anexo_1c')
bins_1c = (read_excel_table(*excel_call)[bins_cols.keys()]
    .astype(bins_cols))

excel_call = (local_path/'api-catalogs.xlsx.lnk', 'banks-bins', 'anexo_1')
bins_1 = (read_excel_table(*(excel_call))
    .loc[:, bins_cols.keys()]
    .astype(bins_cols)
    .set_index('BIN'))

bins_1.update(bins_1c)

bins = (bins_1
    .assign(ID = lambda df: df['Id Institución'].astype(str).str[3:])
    .reset_index())

bins.to_feather(local_path/f'{ctlg_files["bins"]}.feather')


# Continuamos con el catálogo de bancos adquirentes. 

df_types = {'int': int, 'str': str, 'date': 'datetime64[ns]'}

acq_cols_2 = (local_path/'api-catalogs.xlsx.lnk', 'banks-acquiring', 'cols_anexo_29')
acq_cols_1 = read_excel_table(*acq_cols_2)
acq_cols   = {row.nombre: df_types[row.type] 
        for _, row in acq_cols_1.iterrows() if row.type}

acq_call = (local_path/'api-catalogs.xlsx.lnk', 'banks-acquiring', 'anexo_29')
acq_tbl  = (read_excel_table(*acq_call)
    .loc[:, acq_cols.keys()]
    .astype(acq_cols)
    .replace({'ID Adquirente': 0}, pd.NA))


acq_tbl.to_feather(local_path/f"{ctlg_files['acquiring']}.feather")

# Y aquí se sube todo.  

# Las variables se guardan localmente cuando ENV='dev'. 


storage_path = 'product/epic-catalogs/app-services'
resourcer = AzureResourcer(ENV, SERVER)
blob_container = resourcer.get_blob_service()

for each_file in ctlg_files.values(): 
    local_p = local_path/f'{each_file}.feather'
    stg_path = f'{storage_path}/{each_file}.feather'

    the_blob = blob_container.get_blob_client(container='bronze', blob=stg_path)

    with open(local_p, 'rb') as _f: 
        the_blob.upload_blob(_f, overwrite=True)

