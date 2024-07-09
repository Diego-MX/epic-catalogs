"""Mid-tier module that executes the API functions. 
"""
# pylint: disable=no-else-raise
# pylint: disable=too-many-locals

from collections import defaultdict
from json import loads

import clabe
from fastapi.exceptions import HTTPException
import pandas as pd

from src import tools, SITE


ctlg_dir = SITE/'refs/catalogs'

str_to_bool = lambda srs: srs == 'True'

banks_df = (pd.read_feather(ctlg_dir/'national-banks.feather')
    .rename(columns={'banxico_id': 'banxicoId'})
    .assign(spei = lambda df: str_to_bool(df['spei']), 
        portability = lambda df: str_to_bool(df['portability'])))

def zipcode_request(a_request): 
    try:
        the_zipcode  = a_request['zipcode']
        response_dfs = zipcode_query(the_zipcode)
        the_response = zipcode_response(response_dfs)
        if (('warnings' in the_response) and
            ('zipcode'  in the_response['warnings']) and
            (the_response['warnings']['zipcode'][0] == 3)):
            the_detail = the_response['warnings']['zipcode'][1]
            raise HTTPException(404, detail=the_detail)
    except HTTPException as frying_pan:
        raise frying_pan
    except Exception as frying_pan:
        raise HTTPException(500) from frying_pan
    return the_response


def banks_request(include_non_spei):
    try:
        resp_df = banks_df[banks_df['spei']] if include_non_spei else banks_df
        banks_keys = {
            'numberOfRecords' : 'numberOfBanks',
            'attributes'      : 'bankAttributes',
            'recordSet'       : 'banksSet'}
        banks_resp = tools.dataframe_response(resp_df, None, banks_keys)
        banks_resp.pop('pagination')
        return banks_resp

    except Exception as frying_pan:
        raise HTTPException(status_code=500) from frying_pan


def clabe_parse(clabe_key):
    try:
        gfb_code = '072'
        bineo_code = '165'
        
        bank_code = clabe_key[0:3]
        es_indirecto = clabe_key[3:5] == '99'
        gfb_a_bineo = clabe_key[7:9] == '20'

        verificator = clabe.compute_control_digit(clabe_key[:-1])
        if (clabe_key[-1] != verificator):
            raise HTTPException(status_code=404, detail='CLABE is not valid.')

        bank_code = clabe_key[0:3]
        in_banks = (bank_code == banks_df.code)

        if in_banks.sum() != 1:
            raise HTTPException(status_code=404, detail='Bank is not registered or unique.')       

        el_banco = banks_df.loc[in_banks, :]
        
        if (bank_code == gfb_code) and es_indirecto and gfb_a_bineo: 
            el_banco = banks_df.loc[banks_df.code == bineo_code]     
        
        return el_banco.to_dict(orient='records')[0]

    except HTTPException as frying_pan: 
        raise frying_pan

    except Exception as frying_pan:
        raise HTTPException(status_code=500) from frying_pan
    



def card_number_parse(card_num, response_obj='bin'):
    try:
        if len(card_num) != 16:
            raise HTTPException(400, 'Card Number must have 16 digits.')

        # ['Longitud', 'Id Institución', 'Institución', 'Naturaleza', 'Marca',
        # 'Tarjeta Chip', 'BIN Virtual', 'Ac Manual', 'Ac TPV',
        # 'Ac Cashback', 'Ac ATMs', 'Ac Ecommerce', 'Ac Cargos Periódicos',
        # 'Ac Ventas X Teléfono', 'Ac Sucursal', 'Ac Pagos en el Intercambio',
        # 'Ac 3D Secure', 'NFC', 'MST', 'Wallet', 'PAN Din', 'CVV/CVC Din',
        # 'NIP', 'Tokenización', 'Vale', 'Fecha de Alta', 'Procesador']
        # ... ID calculada.
        bin_cols = {
            'Rango'         : 'length',
            'ID'            : 'bankId',
            'banxico_id'    : 'banxicoId',
            'Institución'   : 'bank',
            'Naturaleza'    : 'nature',
            'Marca'         : 'brand'}

        bins_df = (pd.read_feather(ctlg_dir/'national-banks-bins.feather')
            .set_index('BIN')
            .rename(columns=bin_cols)
            .loc[:, bin_cols.values()])
        
        bin_lengths = defaultdict(list)
        for a_bin, length in bins_df['length'].items():
            bin_lengths[length].append(a_bin)

        try_bin = False
        for length in sorted(bin_lengths.keys(), reverse=True):
            try_bin = int(card_num[:length]) in bin_lengths[length]
            if try_bin:
                bin_int = int(card_num[:length])
                the_bin = bins_df.loc[bin_int, :]

                if response_obj == 'bin':
                    pre_response = loads(the_bin.to_json())
                    pre_response['bin'] = str(the_bin.name)
                
                elif response_obj == 'bank':
                    its_bank = banks_df.set_index('banxicoId').loc[the_bin.banxicoId]
                    pre_response = loads(its_bank.to_json())
                    pre_response['banxicoId'] = the_bin.banxicoId
                    pre_response.pop('index')

                return pre_response
        raise HTTPException(status_code=404, detail='Card Bin Not Found.')

    except HTTPException as frying_pan:
        raise frying_pan

    except Exception as frying_pan:
        raise HTTPException(status_code=500) from frying_pan


def bank_acquiring(acquiring_code):
    try: 
        acq_cols = {
            'Institución' : 'name', 
            'ID Adquirente' : 'codeAcquiring'
        }
        acquiring_banks = (pd.read_feather(ctlg_dir/'national-banks-acquiring.feather')
            .rename(columns=acq_cols))

        find_any = (acquiring_banks['codeAcquiring'] == acquiring_code)
        
        if find_any.sum() != 1: 
            raise HTTPException(status_code=404,
                detail='Acquiring Bank is not registered or unique.')
        else: 
            return acquiring_banks[find_any].to_dict(orient='records')[0]

    except HTTPException as frying_pan: 
        raise frying_pan

    except Exception as frying_pan: 
        raise HTTPException(status_code=500) from frying_pan
        
        

#%% Down the Rabbit Hole.

def zipcode_query(a_zipcode):
    try:
        tipo_asenta = pd.read_feather(ctlg_dir/'codigos_drive_tipo_asentamientos.feather')
        ciudades = pd.read_feather(ctlg_dir/'codigos_drive_ciudades.feather')
        municipios =(pd.read_feather(ctlg_dir/'codigos_drive_municipios.feather')
            .assign(cve_mnpio=lambda df: df.c_estado.str.cat(df.c_mnpio)))

        estados = (pd.read_csv(ctlg_dir/'estados_claves.csv')
            .assign(c_estado = lambda df: df.clave.map(str).str.pad(2, fillchar='0'))
            .rename(columns={'nombre': 'd_estado', 'ISO_3166': 'c_estado_iso'})
            .loc[:, ['c_estado', 'd_estado', 'c_estado_iso']])

        las_colonias = (pd.read_feather(ctlg_dir/'codigos_drive.feather')
            .query(f'`d_codigo` == "{a_zipcode}"'))

        mun_edo_0 = (las_colonias
            .groupby(['d_codigo', 'c_estado', 'c_mnpio'])
            .size().to_frame('n_cols').reset_index())

        mun_edo = (mun_edo_0.loc[[mun_edo_0['n_cols'].idxmax()], :]
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

    except Exception as frying_pan:
        into_the_fire = HTTPException(500, str(frying_pan))
        raise into_the_fire from frying_pan


def zipcode_response(nbhd_elems):
    try:
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

        if one_borough:
            zipcode_props = zpcd_df.to_dict(orient='records')[0]
        else: # more than one
            zipcode_props = zpcd_df.to_dict(orient='records')

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

        the_response = zipcode_warnings(pre_response, warnables)
        return the_response

    except Exception as frying_pan:
        raise HTTPException(status_code=500, detail=str(frying_pan)) from frying_pan


def zipcode_warnings(a_response, warnables):
    try:
        warnings = {}
        if   warnables[0]:
            warnings['borough'] = (1, 'No se encontró municipio para CP')
        elif warnables[1]:
            warnings['borough'] = (2, 'Los municipios asociados no son únicos.')

        if   warnables[2]:
            warnings['zipcode'] = (3, 'No se encontraron asentamientos con el CP.')

        b_response = a_response.copy()
        if len(warnings) > 0:
            b_response['warnings'] = warnings
        return b_response
    except Exception as frying_pan:
        raise HTTPException(status_code=500, detail=str(frying_pan)) from frying_pan


