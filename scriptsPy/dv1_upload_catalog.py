# Diego Villamil, EPIC
# CDMX, 11 de noviembre de 2021

# Objetivo. 
# 1. Identificar catálogo fuente por archivo u otro método. 
# 2. Identificar path del catálogo en el datalake. 
# 3. Cargar el catálogo en el datalake.  

from src import tools
import config

SITE = config.SITE


which_ctlg = "national-banks"

path_ctlg = "epic/catalogs/operational/regulatory/national-banks.feather"

# Lo hacemos para bancos, y después generalizamos. 

ctlg_from = (SITE/"refs/catalogs/bancos.xlsx.lnk", "hoja_bancos", "bancos")
ctlg_mid  =  SITE/"refs/catalogs/bancos.feather"


bank_cols = {
    "NOMBRE" : "name", 
    "BANCO"  : "code",  
    "PARAMETRO Activo / Desactivo": "is_active"}

ctlg_df = (tools.read_excel_table(*ctlg_from)
    .rename(columns=bank_cols)
    .loc[:, bank_cols.values()]
    .query("`is_active` == 'A' ")
    .drop(columns="is_active")
    .astype(str)    # Un bug de algo de Arrow. 
    .reset_index(drop=True))
# Link del Bug. 
# https://stackoverflow.com/questions/69578431/how-to-fix-streamlitapiexception-expected-bytes-got-a-int-object-conver

ctlg_df.to_feather(ctlg_mid)





