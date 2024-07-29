
import pandas as pd
from sqlalchemy import text
import time

from src import SITE, tools 
from src.app.exceptions import NotFoundError

catalogs_path = SITE/"refs/catalogs"

def zipcode_request(a_zipcode):
    response_dfs = zipcode_query(a_zipcode)
    the_response = zipcode_response(response_dfs)
    if (('warnings' in the_response) and
        ('zipcode'  in the_response['warnings']) and
        (the_response['warnings']['zipcode'][0] == 3)):
        the_detail = the_response['warnings']['zipcode'][1]
        raise NotFoundError('Zipcode not found', the_detail)
    return the_response


def zipcode_query(a_zipcode):
    """
    Obtención de los datos de zipcode desde la db
    """
    inicio=time.time()

    query_mnpio_estado=text("""
            SELECT d_codigo, d_mnpio, d_estado,
                estados.c_estado,c_estado_iso,cve_mnpio
            FROM ( 
                SELECT mun_edo_0.d_codigo, mun_edo_0.c_estado, 
                    mun_edo_0.c_mnpio, mun_edo_0.n_cols
                FROM (
                    SELECT d_codigo, c_estado, c_mnpio, COUNT(*) AS n_cols
                    FROM codigos_drive
                    WHERE d_codigo = :codigo_postal
                    GROUP BY d_codigo, c_estado, c_mnpio) AS mun_edo_0 
                WHERE mun_edo_0.n_cols = (
                    SELECT MAX(n_cols)
                    FROM ( SELECT COUNT(*) AS n_cols
                        FROM codigos_drive
                        WHERE d_codigo = :codigo_postal
                        GROUP BY d_codigo, c_estado, c_mnpio) AS SubConsulta)) AS colonias
            LEFT JOIN (
                SELECT *, CONCAT(c_estado,c_mnpio) AS cve_mnpio 
                FROM codigos_drive_municipios) AS municipio 
                    ON colonias.c_estado = municipio.c_estado 
                    AND colonias.c_mnpio = municipio.c_mnpio  
            LEFT JOIN (
                SELECT RIGHT('0'+CAST(clave AS VARCHAR(2)),2) AS c_estado,
                        nombre AS d_estado,
                        ISO_3166 AS c_estado_iso
                FROM estados_claves) AS estados 
                    ON colonias.c_estado = estados.c_estado;
            """)
    query_colonias=text("""
                SELECT d_codigo, d_asenta, 
                        d_zona, d_tipo_asenta, 
                        d_ciudad, CONCAT(ciudades.c_estado, ciudades.c_cve_ciudad) AS cve_ciudad
                FROM (SELECT * 
                    FROM codigos_drive 
                    WHERE d_codigo = :codigo_postal) AS colonias
                LEFT JOIN codigos_drive_tipo_asentamientos AS asentamiento
                ON colonias.c_tipo_asenta = asentamiento.c_tipo_asenta
                LEFT JOIN codigos_drive_ciudades AS ciudades 
                ON colonias.c_estado = ciudades.c_estado 
                AND colonias.c_cve_ciudad = ciudades.c_cve_ciudad
                ORDER BY n_asenta DESC;
                """)

    engine_zipcode=tools.get_connection()
    connection_zipcode=engine_zipcode.connect()

    extraccion_mnpio=connection_zipcode.execute(query_mnpio_estado, {"codigo_postal":a_zipcode})
    todos_mnpios=extraccion_mnpio.fetchall()
    mun_edo=pd.DataFrame(todos_mnpios,columns=extraccion_mnpio.keys())

    extraccion_colonia=connection_zipcode.execute(query_colonias,{"codigo_postal":a_zipcode})
    todas_colonias=extraccion_colonia.fetchall()
    sub_cols=pd.DataFrame(todas_colonias,columns=extraccion_colonia.keys())

    connection_zipcode.close()
    engine_zipcode.dispose()

    resp_elements={
        'zipcode_df': mun_edo, 
        'neighborhoods_df': sub_cols}

    fin=time.time()
    print(f"TE: {round(fin-inicio,2)} seg")

    return resp_elements


def zipcode_response(nbhd_elems):
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


def zipcode_warnings(a_response, warnables):
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