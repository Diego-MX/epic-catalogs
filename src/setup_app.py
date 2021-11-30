from datetime import datetime as dt
import pandas as pd

from src import tools
from config import SITE

def upload_catalog(which=None, file_in=None, file_out=None):
    availables = ["national-banks", "banks-bins"]
    if which not in availables:
        raise "Catalog not found."

    elif which == "bank-bins":
        bins_file = SITE/"refs/catalogs/banks-bins.xlsx.lnk"
        
        bins_1   = tools.read_excel_table(bins_file, "Anexo 1",  "anexo_1")
        bins_1c  = tools.read_excel_table(bins_file, "Anexo 1C", "anexo_1c")
        emisores = tools.read_excel_table(bins_file, "Emisores", "emisores")
        
        si_no_cols = ["Tarjeta Chip", "BIN Virtual", "Ac Manual", "Ac TPV", 
            "Ac Cashback", "Ac ATMs", "Ac Ecommerce", "Ac Cargos Periódicos", 
            "Ac Ventas X Teléfono", "Ac Sucursal", "Ac Pagos en el Intercambio", 
            "Ac 3D Secure", "NFC", 'MST', 'Wallet', 'PAN Din', 'CVV/CVC Din', 
            'NIP', 'Tokenización', 'Vale']
        bin_types  = {'Longitud':int, 'Id Institución': int, 
            "Fecha de Alta": 'datetime64[ns]'}
        
        bins_2 = bins_1.set_index("BIN")
        bins_2.update(bins_1c.set_index("BIN"))
        
        bins = (bins_2
            .assign(**{a_col: lambda df: df[a_col] == "SI" for a_col in si_no_cols})
            .astype(bin_types)
            .reset_index()) 

        bins.to_feather(SITE/"refs/catalogs/banks-bins.feather")
        



def setup_geo_catalog():
    pass



