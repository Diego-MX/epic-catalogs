
# pylint: disable=too-few-public-methods
from typing import List

import numpy as np
import pandas as pd
from pydantic import Field

from src.app.exceptions import ValidationError
from src.app.models import CustomModel


class Zipcode(CustomModel):     # alias viene del dataframe de lectura.  
    zipcode    : str = Field(alias='d_codigo')
    state      : str = Field(alias='d_estado')
    state_id   : str = Field(alias='c_estado')
    state_iso  : str = Field(alias='c_estado_iso')
    borough    : str = Field(alias='d_mnpio')
    borough_id : str = Field(alias='cve_mnpio')


class Neighborhood(CustomModel): 
    zipcode : str = Field(alias='d_codigo', min_length=5, max_length=5)
    name    : str = Field(alias='d_asenta')
    zone    : str = Field(alias='d_zona')
    type    : str = Field(alias='d_tipo_asenta')
    city    : str = Field(alias='d_ciudad', default='')
    city_id : str = Field(alias='cve_ciudad')


# No está padre.
class NeighborhoodsRequest(CustomModel): 
    zipcode : str = Field(min_length=5, max_length=5)


# No está padre.
class MetaRequestNbhd(CustomModel): 
    neighborhoodsRequest : NeighborhoodsRequest


# No está padre
class Neighborhoods(CustomModel): 
    numberOfNeighborhoods  : int
    neighborhoodAttributes : List[str]
    neighborhoodsSet       : List[Neighborhood]

    @classmethod
    def from_df(cls, df:pd.DataFrame):
        pre_neighborhoods = [Neighborhood.from_row(nbhr) 
            for _, nbhr in df.iterrows()]
        new_obj = cls(
            numberOfNeighborhoods = len(pre_neighborhoods), 
            neighborhoodAttributes = list(cls.__fields__),
            neighborhoodsSet = pre_neighborhoods)
        return new_obj


# No está padre
class NeighborhoodsResponse(CustomModel): 
    zipcode       : Zipcode
    neighborhoods : Neighborhoods

    @classmethod
    def from_df(cls, df:pd.DataFrame, first_zipcode=False):
        zip_cols = set(ff.alias for ff in Zipcode.__fields__.values())
        zip_equal = np.all(df.loc[:, zip_cols] == df.loc[0, zip_cols])
        if not (zip_equal or first_zipcode): 
            error_call = dict(
                name="NbhdResponseValidation", 
                detail="Not all zipcodes are equal.")
            raise ValidationError(**error_call)
        
        the_object = cls(
            zipcode = Zipcode.from_row(df.loc[0, zip_cols]), 
            neighborhoods = Neighborhoods.from_df(df))
        return the_object


class ZipcodeProcessor: 
    def __init__(self, engine:str=None): 
        self.engine = engine
        self.zipcode = None 
        self.warnings = []

    def query_zipcode(self, zipcode:str) -> pd.DataFrame: 
        pass

    def process_result(self, dataframe:pd.DataFrame): 
        pass

    def to_json(self, model:CustomModel): 
        pass

