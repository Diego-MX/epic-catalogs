from json import loads
from collections import defaultdict
import pandas as pd

from fastapi.exceptions import HTTPException

import clabe

from src import tools
from config import SITE

ctlg_dir = SITE/"refs/catalogs"
banks_df = pd.read_feather(ctlg_dir/"national-banks.feather")


def zipcode_request(a_request): 
    try: 
        the_zipcode  = a_request["zipcode"]
        response_dfs = zipcode_query(the_zipcode)
        the_response = zipcode_response(response_dfs)
        if (("warnings" in the_response) and 
            ("zipcode"  in the_response["warnings"]) and 
            (the_response["warnings"]["zipcode"][0] == 3)):
            detail = the_response["warnings"]["zipcode"][1]
            code   = 404
        else:
            code = 200
    
    except Exception as exc:
        detail = str(exc)
        the_response = {"exception": detail}
        code = 500

    if code == 200: 
        return the_response
    elif code != 200: 
        an_exception = HTTPException(status_code=code, detail=detail)
        raise an_exception


def banks_request(): 
    try:
        banks_keys = { 
            "numberOfRecords" : "numberOfBanks",
            "attributes"      : "bankAttributes",
            "recordSet"       : "banksSet"}
        banks_resp = tools.dataframe_response(banks_df, None, banks_keys)
        code       = 200
    except Exception as exc:
        detail     = str(exc)
        banks_resp = {"an_exception": detail}
        code       = 500

    if code == 200: 
        return banks_resp
    elif code != 200: 
        raise HTTPException(status_code=code, detail=detail)


def clabe_parse(clabe_key): 
    try:
        is_valid  = clabe.validate_clabe(clabe_key)
        bank_code = clabe_key[0:3]
        
        in_banks = (bank_code == banks_df.code)
        pre_resp = banks_df.loc[in_banks, :].to_dict(orient="records")

        if   is_valid and (in_banks.sum() == 1): 
            bank_resp = pre_resp[0]
            code = 200
        elif is_valid and (in_banks.sum() != 1): 
            detail = "Associated Bank key is not registered or unique."
            code = 404
        elif not is_valid:
            detail = "CLABE is not valid."
            code = 404
        
    except Exception as exc: 
        detail    = str(exc)
        bank_resp = {"an_exception": detail}
        code      = 500

    if code == 200: 
        return bank_resp
    elif code != 200: 
        an_exception = HTTPException(status_code=code, detail=detail)
        raise an_exception


def card_number_parse(card_num): 
    try:
        if len(card_num) != 16:
            raise "Card Number has 16 digits."

        # ["Longitud", "Id Institución", "Institución", "Naturaleza", "Marca",
        # "Tarjeta Chip", "BIN Virtual", "Ac Manual", "Ac TPV", 
        # "Ac Cashback", "Ac ATMs", "Ac Ecommerce", "Ac Cargos Periódicos", 
        # "Ac Ventas X Teléfono", "Ac Sucursal", "Ac Pagos en el Intercambio", 
        # "Ac 3D Secure", "NFC", "MST", "Wallet", "PAN Din", "CVV/CVC Din", 
        # "NIP", "Tokenización", "Vale", "Fecha de Alta", "Procesador"]
        # ... ID calculada.
        bin_cols = {
            "Longitud"      : "length", 
            "ID"            : "bankId", 
            "Institución"   : "bank", 
            "Naturaleza"    : "nature", 
            "Marca"         : "brand"}
                
        bins_df = (pd.read_feather(ctlg_dir/"national-banks-bins.feather")
            .set_index('BIN')
            .rename(columns=bin_cols)
            .loc[:, bin_cols.values()])

        bin_lengths = defaultdict(list)
        for bin, length in bins_df["length"].items():
            bin_lengths[length].append(bin)

        try_bin = False
        for length in sorted(bin_lengths.keys(), reverse=True):
            try_bin = int(card_num[:length]) in bin_lengths[length]

            if try_bin: 
                code  = 200
                bin_int = int(card_num[:length])
                the_bin = bins_df.loc[bin_int, :]
                pre_response = loads(the_bin.to_json())
                pre_response["bin"] = str(the_bin.name)
                break
        else:
            code = 404
            detail = "Card Bin Not Found."
        
    except Exception as exc: 
        detail = str(exc)
        code   = 500
        pre_response = {"an_exception": detail}
        
    if code == 200:
        return pre_response
    elif code != 200: 
        an_exception = HTTPException(status_code=code, detail=detail)
        raise an_exception



#%% Down the Rabbit Hole. 

def zipcode_query(a_zipcode): 
    tipo_asenta = pd.read_feather(ctlg_dir/"codigos_drive_tipo_asentamientos.feather")
    ciudades    = pd.read_feather(ctlg_dir/"codigos_drive_ciudades.feather")
    municipios  =(pd.read_feather(ctlg_dir/"codigos_drive_municipios.feather")
        .assign(cve_mnpio=lambda df: df.c_estado.str.cat(df.c_mnpio)))
    estados     =(pd.read_csv(    ctlg_dir/"estados_claves.csv")
        .assign(c_estado = lambda df: df.clave.map(str).str.pad(2, fillchar="0"))
        .rename(columns={"nombre": "d_estado", "ISO_3166": "c_estado_iso"})
        .loc[:, ["c_estado", "d_estado", "c_estado_iso"]])

    las_colonias = (pd.read_feather(ctlg_dir/"codigos_drive.feather")
        .query(f"`d_codigo` == '{a_zipcode}'"))
    hay_colonias = las_colonias.shape[0] > 1

    if hay_colonias:
        mun_estado = (las_colonias[["d_codigo", "c_estado", "c_mnpio"]]
            .drop_duplicates()
            .merge(municipios, on=["c_estado", "c_mnpio"], how="left")
            .merge(estados, on="c_estado", how="left")
            .loc[:, ["d_codigo", "d_mnpio", "d_estado", 
                "c_estado", "c_estado_iso", "cve_mnpio"]])
    else:
        mun_estado = (municipios
            .loc[(municipios.min_cp <= a_zipcode) & (a_zipcode <= municipios.max_cp), :] 
            .assign(d_codigo=a_zipcode)
            .merge(estados, on="c_estado", how="left")
            .loc[:, ["d_codigo", "d_mnpio", "d_estado", 
                "c_estado", "c_estado_iso", "cve_mnpio"]])
        
    sub_colonias = (las_colonias
        .merge(tipo_asenta, on="c_tipo_asenta", how="left")
        .merge(ciudades, on=["c_estado", "c_cve_ciudad"], how="left")
        .sort_values("n_asenta", ascending=False)
        .assign(cve_ciudad = lambda df: df.c_estado.str.cat(df.c_cve_ciudad))
        .loc[:, ["d_codigo", "d_asenta", "d_zona", "d_tipo_asenta", "d_ciudad", 
                "cve_ciudad"]] )

    resp_elements = {
        "zipcode_df"        : mun_estado, 
        "neighborhoods_df"  : sub_colonias}
    return resp_elements


def zipcode_response(nbhd_elems):
    translator = {
        "d_codigo"      : "zipcode",    "d_asenta"      : "name", 
        "d_tipo_asenta" : "type",       "d_zona"        : "zone",
        "d_ciudad"      : "city",       "cve_ciudad"    : "city_id", 
        "d_estado"      : "state",      "c_estado"      : "state_id", 
                                        "c_estado_iso"  : "state_iso",
        "d_mnpio"       : "borough",    "cve_mnpio"     : "borough_id"}

    zpcd_df = nbhd_elems.get("zipcode_df").rename(columns=translator)
    nbhd_df = nbhd_elems.get("neighborhoods_df").rename(columns=translator)

    no_borough    = (zpcd_df.shape[0] == 0)
    one_borough   = (zpcd_df.shape[0] == 1)
    multi_borough = (zpcd_df.shape[0] >  1)
    no_nghbrhoods = (nbhd_df.shape[0] == 0)
    warnables     = (no_borough, multi_borough, no_nghbrhoods)

    if one_borough:
        zipcode_props = zpcd_df.to_dict(orient="records")[0]
    else: # more than one
        zipcode_props = zpcd_df.to_dict(orient="records")

    nbhd_cols = pd.DataFrame(data={
            "nombre" : ["zipcode", "name", "zone", "type", "city", "city_id"], 
            "dtipo"  : "character"})

    nbhd_keys = { "numberOfRecords" : "numberOfNeighborhoods",
                  "attributes"      : "neighborhoodAttributes",
                  "recordSet"       : "neighborhoodsSet",
                  "pagination"      : "neighborhoodsPagination"}

    nbhd_dict = tools.dataframe_response(nbhd_df, nbhd_cols, nbhd_keys, drop_nas=False)
    
    pre_response = {
        "zipcode"       : zipcode_props, 
        "neighborhoods" : nbhd_dict }

    the_response = zipcode_warnings(pre_response, warnables)
    return the_response


def zipcode_warnings(a_response, warnables):
    warnings = {}
    if   warnables[0]:
        warnings["borough"] = (1, "No se encontró municipio para CP")
    elif warnables[1]:
        warnings["borough"] = (2, "Los municipios asociados no son únicos.")

    if   warnables[2]:
        warnings["zipcode"] = (3, "No se encontraron asentamientos con el CP.")
    
    b_response = a_response.copy()
    if len(warnings) > 0: 
        b_response["warnings"] = warnings 

    return b_response
