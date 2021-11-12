
import pandas as pd

from flask import jsonify
from src import tools
import config

SITE = config.SITE
ctlg_dir  = SITE/"refs/catalogs"
    
    

def zipcode_request(request): 
    try: 
        the_zipcode  = request.get("zipcode")
        response_dfs = zipcode_query(the_zipcode)
        the_response = zipcode_response(response_dfs)
        if (("warnings" in the_response) and 
            ("zipcode"  in the_response["warnings"]) and 
            (the_response["warnings"]["zipcode"][0] == 3)):
            code = 404
        else:
            code = 200
    
    except Exception as exc:
        the_response = {"exception": str(exc)}
        code = 500
    return (jsonify(the_response), code)

    
def bank_request(request): 
    banks_df = pd.read_feather(ctlg_dir/"bancos.feather")

    bank_keys = { 
        "numberOfRecords" : "numberOfBanks",
        "attributes"      : "bankAttributes",
        "recordSet"       : "banksSet"}

    bank_resp = tools.dataframe_response(banks_df, None, bank_keys)
    return (bank_resp, 200)



#%% Further Down the Rabbit Hole. 


def zipcode_query(a_zipcode): 
    tipo_asenta = pd.read_feather(ctlg_dir/"codigos_drive_tipo_asentamientos.feather")
    ciudades    = pd.read_feather(ctlg_dir/"codigos_drive_ciudades.feather")
    municipios  = pd.read_feather(ctlg_dir/"codigos_drive_municipios.feather")
    estados     =(pd.read_csv(    ctlg_dir/"estados_claves.csv")
        .assign(c_estado = lambda df: df.clave.map(str).str.pad(2, fillchar="0"))
        .loc[:, ["c_estado", "nombre"]]
        .rename(columns={"nombre": "d_estado"}))

    las_colonias = (pd.read_feather(ctlg_dir/"codigos_drive.feather")
        .query(f"`d_codigo` == '{a_zipcode}'"))
    hay_colonias = (las_colonias.shape[0] > 1)

    if hay_colonias:
        mun_estado = (las_colonias[["d_codigo", "c_estado", "c_mnpio"]].drop_duplicates()
            .merge(municipios, on=["c_estado", "c_mnpio"], how="left")
            .merge(estados, on="c_estado", how="left")
            .assign(cve_mnpio=lambda df: df.c_estado.str.cat(df.c_mnpio))
            .loc[:, ["d_codigo", "d_mnpio", "d_estado", "c_estado", "cve_mnpio"]])
    else:
        mun_estado = (municipios
            .assign(cve_mnpio=lambda df: df.c_estado.str.cat(df.c_mnpio))
            .loc[(municipios.min_cp <= a_zipcode) & (a_zipcode <= municipios.max_cp), 
                  ["c_estado", "cve_mnpio", "d_mnpio"]]
            .merge(estados, on="c_estado", how="left"))
        
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
            "database"  : ["zipcode", "name", "zone", "type", "city", "city_id"], 
            "dtipo"     : "character"})

    nbhd_keys = { "numberOfRecords" : "numberOfNeighborhoods",
                  "attributes"      : "neighborhoodAttributes",
                  "recordSet"       : "neighborhoodsSet",
                  "pagination"      : "neighborhoodsPagination"}

    nbhd_dict = tools.dataframe_response(nbhd_df, nbhd_cols, nbhd_keys)
    
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
