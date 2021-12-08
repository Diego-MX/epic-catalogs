# Diego Villamil, EPIC
# CDMX, 1 de diciembre de 2021

# From Excel to Feather to Blob

import os

from azure.identity import ClientSecretCredential 
from azure.storage.blob import BlobServiceClient

from src.tools import read_excel_table
from dotenv import load_dotenv

load_dotenv(override=True)
from config import SITE, ENV_VARS


#%%  General considerations
local_path   = SITE/"refs/catalogs"
storage_path = "product/epic-catalogs/app-services"

ctlg_files = {
    "banks"  : "national-banks.feather",
    "plazas" : "national-banks-plazas.feather",
    "bins"   : "national-banks-bins.feather"
}

#%% Banks

excel_call  = (local_path/"api-catalogs.xlsx.lnk", "banks", "tabla_297")
df_colnames = {
    "NOMBRE" : "name", 
    "CLAVE"  : "code",  
    "PARAMETRO Activo / Desactivo": "is_active", 
    "Tipo banco" : "type", 
    "warning": "warning"}

ctlg_df = (read_excel_table(*excel_call)
    .rename(columns=df_colnames)
    .assign(warning=lambda df: (df.is_active != 'A'))
    .loc[:, df_colnames.values()]
    .drop(columns=["is_active", "type"])
    .astype(str)    
    .reset_index(drop=True))

ctlg_df.to_feather(local_path/ctlg_files["banks"])

#%% Plazas is almost the same. 

excel_call = (local_path/"api-catalogs.xlsx.lnk", "banks", "plazas_w")

df_colnames = {
    "Nombre" : "name",
    "Plaza"  : "code"}

# Setup columns
ctlg_df = (read_excel_table(*excel_call)
    .rename(columns=df_colnames)
    .assign(code=lambda df: df.code.map(str).str.pad(3, fillchar="0")))

ctlg_df.to_feather(local_path/ctlg_files["plazas"])


#%% Bins requires some column manipulation

the_types   = {"integer": int, "character": str, "date": "datetime64[ns]"}

excel_call = [local_path/"api-catalogs.xlsx.lnk", "banks-bins", "cols_anexo1"]
bins_cols_ = read_excel_table(*(excel_call))
bins_cols  = (bins_cols_.loc[~bins_cols_.Tipo.isnull(), ]
    .set_index("Columna")["Tipo"])

excel_call = [local_path/"api-catalogs.xlsx.lnk", "banks-bins", "anexo_1c"]
bins_1c = (read_excel_table(*(excel_call))
    .loc[:, bins_cols.keys()]
    .astype({k: the_types[v] for (k, v) in bins_cols.items()}))

excel_call = [local_path/"api-catalogs.xlsx.lnk", "banks-bins", "anexo_1"]
bins_1 = (read_excel_table(*(excel_call))
    .loc[:, bins_cols.keys()]
    .astype({k: the_types[v] for (k, v) in bins_cols.items()})
    .set_index("BIN"))
bins_1.update(bins_1c)

bins = bins_1.reset_index()

bins.to_feather(local_path/ctlg_files["bins"])


#%% And now upload all. 

credential = ClientSecretCredential(**{k: os.getenv(v) 
        for (k, v) in ENV_VARS["app_sp"].items()})

blob_container = BlobServiceClient("https://lakehylia.blob.core.windows.net/", credential)

for each_file in ctlg_files.values(): 
    local_p  = local_path/each_file
    stg_path = f"{storage_path}/{each_file}"

    the_blob = blob_container.get_blob_client(container="bronze", blob=stg_path)

    with open(local_p, "rb") as _f: 
        the_blob.upload_blob(_f)

