
import pandas as pd

from src import SITE, tools 
from src.app.exceptions import NotFoundError

from . import models

catalogs_path = SITE/"refs/catalogs"


def zipcode_request(a_zipcode:str) -> dict: # NeighborhoodsResponse
    """Wrapper de lo demás."""
    response_dfs = zipcode_query(a_zipcode)
    the_response = zipcode_response(response_dfs)
    if (('warnings' in the_response) and
        ('zipcode'  in the_response['warnings']) and
        (the_response['warnings']['zipcode'][0] == 3)):
        the_detail = the_response['warnings']['zipcode'][1]
        raise NotFoundError('Zipcode not found', the_detail)
    return the_response


def zipcode_query(a_zipcode:str) -> dict:  # Two Dataframes.
    """Returns Dict with keys: 'zipcodes_df', 'nieghborhoods_df'"""
    tipo_asenta = pd.read_feather(catalogs_path/'codigos_drive_tipo_asentamientos.feather')
    ciudades = pd.read_feather(catalogs_path/'codigos_drive_ciudades.feather')
    municipios =(pd.read_feather(catalogs_path/'codigos_drive_municipios.feather')
        .assign(cve_mnpio=lambda df: df.c_estado.str.cat(df.c_mnpio)))
    estados = (pd.read_csv(catalogs_path/'estados_claves.csv')
        .assign(c_estado = lambda df: df.clave.map(str).str.pad(2, fillchar='0'))
        .rename(columns={'nombre': 'd_estado', 'ISO_3166': 'c_estado_iso'})
        .loc[:, ['c_estado', 'd_estado', 'c_estado_iso']])
    las_colonias = (pd.read_feather(catalogs_path/'codigos_drive.feather')
        .query(f'`d_codigo` == "{a_zipcode}"'))

    if las_colonias.shape[0] == 0: 
        cols_msg = f"Empty list of neighborhoods at '{a_zipcode}'"
        raise NotFoundError('Colonias Not Found', cols_msg)
    
    mun_edo = (las_colonias
        .groupby(['d_codigo', 'c_estado', 'c_mnpio'])
        .size().to_frame('n_cols').reset_index()    
        # .loc[[mun_edo_0['n_cols'].idxmax()], :]
        .sort_values('n_cols', ascending=False).loc[[0], :]
        .merge(municipios, how='left', on=['c_estado', 'c_mnpio'])
        .merge(estados, how='left', on='c_estado')
        .loc[:, ['d_codigo', 'd_mnpio', 'd_estado', 
            'c_estado', 'c_estado_iso', 'cve_mnpio']])

    sub_cols = (las_colonias
        .merge(tipo_asenta, on='c_tipo_asenta', how='left')
        .merge(ciudades, on=['c_estado', 'c_cve_ciudad'], how='left')
        .sort_values('n_asenta', ascending=False)
        .assign(cve_ciudad = lambda df: df.c_estado.str.cat(df.c_cve_ciudad))
        .loc[:, ['d_codigo', 'd_asenta', 'd_zona', 
            'd_tipo_asenta', 'd_ciudad', 'cve_ciudad']])

    resp_elements = {
        'zipcode_df': mun_edo, 
        'neighborhoods_df': sub_cols}
    return resp_elements


def zipcode_response(nbhd_elems:dict) -> dict:
    """
    In:  [zipcode_df, neighborhoods_df]-keyed dict.  
    Out: Explore warnings and add if necessary.
    """
    translator = {
        'd_codigo'      : 'zipcode',    'd_asenta'      : 'name',
        'd_tipo_asenta' : 'type',       'd_zona'        : 'zone',
        'd_ciudad'      : 'city',       'cve_ciudad'    : 'city_id',
        'd_estado'      : 'state',      'c_estado'      : 'state_id',
                                        'c_estado_iso'  : 'state_iso',
        'd_mnpio'       : 'borough',    'cve_mnpio'     : 'borough_id'}

    zpcd_df = nbhd_elems.get('zipcode_df').rename(columns=translator)
    nbhd_df = nbhd_elems.get('neighborhoods_df').rename(columns=translator)

    no_borough    = (zpcd_df.shape[0] == 0)
    one_borough   = (zpcd_df.shape[0] == 1)
    multi_borough = (zpcd_df.shape[0] >  1)
    no_nghbrhoods = (nbhd_df.shape[0] == 0)
    warnables     = (no_borough, multi_borough, no_nghbrhoods)

    the_boroughs = zpcd_df.to_dict(orient='records')
    zipcode_props = the_boroughs[0] if one_borough else the_boroughs
    
    nbhd_cols = pd.DataFrame(data={
            'nombre' : ['zipcode', 'name', 'zone', 'type', 'city', 'city_id'],
            'dtipo'  : 'character'})

    nbhd_keys = {
        'numberOfRecords' : 'numberOfNeighborhoods',
        'attributes'      : 'neighborhoodAttributes',
        'recordSet'       : 'neighborhoodsSet',
        'pagination'      : 'neighborhoodsPagination'}

    nbhd_dict = tools.dataframe_response(nbhd_df, nbhd_cols, nbhd_keys, drop_nas=False)

    pre_response = {
        'zipcode'       : zipcode_props,
        'neighborhoods' : nbhd_dict }
    return zipcode_warnings(pre_response, warnables)


def zipcode_warnings(a_response:dict, warnables:list) -> dict:
    """Add 'warnings' key to Dict if warnings."""
    warnings = {}
    if warnables[0]:
        warnings['borough'] = (1, 'No se encontró municipio para CP')
    elif warnables[1]:
        warnings['borough'] = (2, 'Los municipios asociados no son únicos.')
    if warnables[2]:
        warnings['zipcode'] = (3, 'No se encontraron asentamientos con el CP.')
    b_response = a_response.copy()
    if len(warnings) > 0:
        b_response['warnings'] = warnings
    return b_response


def one_sql_query(a_zipcode:str) -> pd.DataFrame: 
    # estados:  ['clave', 'd_estado', 'ABR', 'Abr_1', 'ABR_2', 'renapo', 'c_estado_iso',
    #           'drive', 'gobmx', 'marco_geo', 'min_cp', 'max_cp', 'clave_2']
    # muns:     ['c_estado', 'c_mnpio', 'd_mnpio', 'min_cp', 'max_cp']
    # ciudades: ['c_estado', 'c_cve_ciudad', 'd_ciudad']
    # tipos_a:  ['c_tipo_asenta', 'd_tipo_asenta', 'n_asenta']
    # colonias: ['d_codigo', 'd_asenta', 'd_zona', 'c_estado', 'c_mnpio', 'c_cve_ciudad',
    #           'c_tipo_asenta']
    estados = (pd.read_csv(catalogs_path/'estados_claves.csv')
        .rename(columns={'nombre': 'd_estado', 'ISO_3166': 'c_estado_iso'})
        .assign(c_estado=lambda df: df.clave.map('{:02f}.format')))
    municipios = pd.read_feather(catalogs_path/'codigos_drive_municipios.feather')
    ciudades = pd.read_feather(catalogs_path/'codigos_drive_ciudades.feather')
    tipo_asenta = pd.read_feather(catalogs_path/'codigos_drive_tipo_asentamientos.feather')
    colonias = pd.read_feather(catalogs_path/'codigos_drive.feather')

    # En caso de múltiples municipios, se toma el que tenga más asentamientos. 
    one_query = (colonias.query(f'`d_codigo` == "{a_zipcode}"')
        .merge(municipios, how='left', on=['c_estado', 'c_mnpio'])
        .merge(estados, how='left', on='c_estado')
        .merge(ciudades, how='left', on=['c_estado', 'c_cve_ciudad'])
        .merge(tipo_asenta, how='left', on='c_tipo_asenta')
        .assign(cve_ciudad = lambda df: df.c_estado.str.cat(df.c_cve_ciudad), 
            cve_mun = lambda df: df.c_estado.str.cat(df.c_mnpio)))
    return one_query


def process_query(a_df:pd.DataFrame): 
    if a_df.shape[0] == 0: 
        raise NotFoundError('Colonias Not Found', "Empty list of neighborhoods")
    
    ok_muns = ~a_df['d_mnpio'].isna()
    if ~a_df.any(ok_muns): 
        raise NotFoundError('Boroughs Not Found', "Cannot assign municipality")

    return models.NeighborhoodsResponse.from_df(a_df)
