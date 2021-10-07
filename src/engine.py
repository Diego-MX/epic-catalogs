import os
from pathlib import Path

import pandas as pd

from flask import jsonify
from src.tools import dataframe_response

SITE = Path(__file__).parents[1] if "__file__" in globals() else Path(os.getcwd())


def process_request(request): 

    response_dfs = query_catalogs(request.get("zipcode"))    
    the_response = manage_response(response_dfs)
    return (jsonify(the_response), 200)

    

def query_catalogs(a_zipcode): 
    ctlg_dir  = SITE/"refs"/"catalogs"
    
    tipo_asenta = pd.read_feather(ctlg_dir/"codigos_drive_tipo_asentamientos.feather")
    ciudades    = pd.read_feather(ctlg_dir/"codigos_drive_ciudades.feather")
    municipios  = pd.read_feather(ctlg_dir/"codigos_drive_municipios.feather")
    estados     = (pd.read_csv(ctlg_dir/"estados_claves.csv")
        .assign(clave = lambda df: df.clave.map(str).str.pad(2, fillchar="0"))
        .loc[:, ["clave", "nombre"]]
        .rename(columns={ "clave": "c_estado", "nombre": "d_estado"}))


    las_colonias = (pd.read_feather(ctlg_dir/"codigos_drive.feather")
        .query(f"`d_codigo` == '{a_zipcode}'"))

    mun_estado = (las_colonias[["d_codigo", "c_estado", "c_mnpio"]].drop_duplicates()
        .merge(municipios, on=["c_estado", "c_mnpio"], how="left")
        .merge(estados, on="c_estado", how="left")
        .loc[:, ["d_codigo", "d_mnpio", "d_estado"]])

    sub_colonias = (las_colonias
        .merge(tipo_asenta, on="c_tipo_asenta", how="left")
        .merge(ciudades, on=["c_estado", "c_cve_ciudad"], how="left")
        .sort_values("n_asenta", ascending=False)
        .loc[:, ["d_codigo", "d_asenta", "d_zona", "d_tipo_asenta", "d_ciudad"]] )

    resp_elements = {"zipcode_df": mun_estado, "neighborhoods_df": sub_colonias}
    return resp_elements


def manage_response(nbhd_elems):
    zipcode_df = nbhd_elems.get("zipcode_df")
    if zipcode_df.shape[0] == 1:
        zipcode_dict = zipcode_df.rename(columns={
            "d_codigo"      : "code",
            "d_estado"      : "state", 
            "d_mnpio"       : "municipality"}).to_dict("list")
        zipcode_properties = {key:val[0] for key,val in zipcode_dict.items()}
        
    nbhd_df   = (nbhd_elems.get("neighborhoods_df").rename(columns={
            "d_codigo"      : "zipcode",
            "d_asenta"      : "name",
            "d_tipo_asenta" : "type",
            "d_zona"        : "zone",
            "d_ciudad"      : "city"}))

    nbhd_cols = pd.DataFrame(data={
        "database":["d_codigo", "d_asenta", "d_zona", "d_tipo_asenta", "d_ciudad"], 
        "dtipo" : "character"})

    nbhd_keys = { "numberOfRecords" : "numberOfNeighborhoods",
                  "attributes"      : "neighborhoodAttributes",
                  "recordSet"       : "neighborhoodsSet",
                  "pagination"      : "neighborhoodsPagination"}

    nbhd_dict = dataframe_response(nbhd_df, nbhd_cols, nbhd_keys)
    nbhd_dict["neighborhoodsPagination"] = False
    the_response = {
        "zipcode"       : zipcode_properties, 
        "neighborhoods" : nbhd_dict }
    return the_response










