
# pylint: disable=too-few-public-methods
from typing import List

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from src.app.exceptions import ValidationError


class CustomModel(BaseModel):
    """Esta clase surgió complicadamente.  
    Al utilizar 'alias' para leer la data, FastAPI convierte los campos en sus alias
    y entonces marcaba error.  
    Últimadamente no he podido deshacerme de los errores ResponseValidation, pero 
    sí me gustó dejar el CustomModel para centralizar algunos comportamientos. 
    """
    def to_dict(self):
        def to_original(data):
            if isinstance(data, BaseModel):
                original_dict = {ff.name: to_original(getattr(data, field.alias))
                    for ff in data.__fields__.values()}
                return original_dict
            if isinstance(data, dict):
                return {kk: to_original(vv) for kk, vv in data.items()}
            if isinstance(data, list):
                return [to_original(ll) for ll in data]
            return data
        return to_original(self)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {BaseModel: lambda v: v.to_dict()}

    @classmethod
    def from_row(cls, row:pd.Series):
        return cls(**row.to_dict())


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

