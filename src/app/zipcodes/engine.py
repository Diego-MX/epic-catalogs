
import time
import pandas as pd
from sqlalchemy import text, select, func, and_
from sqlalchemy.orm import sessionmaker, aliased

from src import SITE, tools
from src.app.exceptions import NotFoundError
from . import models

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
    engine = tools.get_connection()
    sesion = sessionmaker(bind=engine) # ORM
    session = sesion()

    codigos_drive = aliased(models.CodigosDrive, name="colonias")
    municipio = aliased(models.CodigosDriveMunicipios, name="municipios")
    estados = aliased(models.EstadosClaves, name="estados")

    mun_edo_0 = (select(codigos_drive.d_codigo,
                        codigos_drive.c_estado,
                        codigos_drive.c_mnpio,
                        func.count().label("n_cols"))
                .where(codigos_drive.d_codigo == a_zipcode)
                .group_by(codigos_drive.d_codigo,
                        codigos_drive.c_estado,
                        codigos_drive.c_mnpio)
                .subquery())

    subconsulta = (select(func.max(mun_edo_0.c.n_cols).label("n_cols"))
                    .scalar_subquery())

    colonias=(select(mun_edo_0)
                        .where(mun_edo_0.c.n_cols == subconsulta)
                        .subquery())

    consulta = (select(colonias.c.d_codigo,
                    municipio.d_mnpio,
                    estados.nombre.label("d_estado"),
                    colonias.c.c_estado,
                    estados.ISO_3166.label("c_estado_iso"),
                    func.concat(colonias.c.c_estado,
                    colonias.c.c_mnpio).label("cve_mnpio"))
                .select_from(colonias
                    .outerjoin(municipio,
                        and_(colonias.c.c_estado == municipio.c_estado,
                            colonias.c.c_mnpio == municipio.c_mnpio))
                    .outerjoin(estados,colonias.c.c_estado == estados.clave)
                            )
                )

    pre_resultado = session.execute(consulta)
    resultado = pre_resultado.fetchall()
    mun_edo=pd.DataFrame(resultado,columns=pre_resultado.keys())

    asentamiento = aliased(models.CodigosDriveTipoAsentamientos, name="asentamiento")
    ciudades = aliased(models.CodigosDriveCiudades, name="ciudades")

    colonias = (select(codigos_drive)
                .where(codigos_drive.d_codigo == a_zipcode)
                .subquery())

    consulta = (select(colonias.c.d_codigo,
                    colonias.c.d_asenta,
                    colonias.c.d_zona,
                    asentamiento.d_tipo_asenta,
                    ciudades.d_ciudad,
                    func.concat(ciudades.c_estado, ciudades.c_cve_ciudad).label('cve_ciudad')
                    )
                .select_from(colonias
                            .join(asentamiento,
                                        colonias.c.c_tipo_asenta == asentamiento.c_tipo_asenta)
                            .join(ciudades, and_(colonias.c.c_estado == ciudades.c_estado,
                                                colonias.c.c_cve_ciudad == ciudades.c_cve_ciudad)))
                .order_by(asentamiento.n_asenta.desc()))

    pre_resultado = session.execute(consulta)
    resultado = pre_resultado.fetchall()
    sub_cols=pd.DataFrame(resultado,columns=pre_resultado.keys())

    engine.dispose()
    session.close()

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

# End-of-file (EOF)
