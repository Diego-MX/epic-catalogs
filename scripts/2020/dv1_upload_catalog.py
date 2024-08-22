# Diego Villamil, EPIC
# CDMX, 11 de noviembre de 2021

# Lectura: refs/catalogos/api-catalogs.xlsx -> (tabla_297, plazas_w)
# Write:   (national-banks|banks-plazas).feather

# Objetivo. 
# 1. Identificar catálogo fuente por archivo u otro método. 
# 2. Identificar path del catálogo en el datalake. 
# 3. Cargar el catálogo en el datalake.  

from src import tools
from config import SITE



which_ctlg = "national-banks"

path_ctlg = "epic/catalogs/operational/regulatory/national-banks.feather"

# Lo hacemos para bancos, y después generalizamos. 

bank      = (SITE/"refs/catalogs/api-catalogs.xlsx.lnk", "banks-aux", "tabla_297")
plazas    = (SITE/"refs/catalogs/api-catalogs.xlsx.lnk", "banks-aux", "plazas_w")
ctlg_mid  =  SITE/"refs/catalogs/national-banks.feather"
plaza_mid =  SITE/"refs/catalogs/banks-plazas.feather"

bank_cols = {
    "NOMBRE" : "name", 
    "CLAVE"  : "code",  
    "PARAMETRO Activo / Desactivo": "is_active", 
    "Tipo banco" : "type", 
    "warning": "warning"}

plazas_cols = {
    "Nombre" : "name",
    "Plaza"  : "code"}

ctlg_df = (tools.read_excel_table(*bank)
    .rename(columns=bank_cols)
    .assign(warning=lambda df: (df.is_active != 'A'))
    .loc[:, bank_cols.values()]
    .drop(columns=["is_active", "type"])
    .astype(str)    
    .reset_index(drop=True))
# Link del Bug. 
# https://stackoverflow.com/questions/69578431/how-to-fix-streamlitapiexception-expected-bytes-got-a-int-object-conver

ctlg_df.to_feather(ctlg_mid)

ctlg_2 = (tools.read_excel_table(*plazas)
    .rename(columns=plazas_cols)
    .assign(code=lambda df: df.code.map(str).str.pad(3, fillchar="0")))

ctlg_2.to_feather(plaza_mid)

