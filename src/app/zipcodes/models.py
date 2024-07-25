
# pylint: disable=too-few-public-methods
from typing import List

import numpy as np
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
        def convert_to_original(data):
            if isinstance(data, BaseModel):
                return {field.name: convert_to_original(getattr(data, field.alias))
                        for field in data.__fields__.values()}
            if isinstance(data, dict):
                return {key: convert_to_original(value) for key, value in data.items()}
            if isinstance(data, list):
                return [convert_to_original(item) for item in data]
            return data
        return convert_to_original(self)
    class Config:
        allow_population_by_field_name = True
        json_encoders = {BaseModel: lambda v: v.to_dict()}


class Zipcode(CustomModel):     # alias viene del dataframe de lectura.  
    zipcode    : str = Field(alias='d_codigo')
    state      : str = Field(alias='d_estado')
    state_id   : str = Field(alias='c_estado')
    state_iso  : str = Field(alias='c_estado_iso')
    borough    : str = Field(alias='d_mnpio')
    borough_id : str = Field(alias='cve_mnpio')

    @classmethod
    def from_row(cls, row): 
        return cls(**row.to_dict())

class Neighborhood(CustomModel): 
    zipcode : str = Field(alias='d_codigo', min_length=5, max_length=5)
    name    : str = Field(alias='d_asenta')
    zone    : str = Field(alias='d_zona')
    type    : str = Field(alias='d_tipo_asenta')
    city    : str = Field(alias='d_ciudad', default='')
    city_id : str = Field(alias='cve_ciudad')

    @classmethod
    def from_row(cls, row):
        return cls(**row.to_dict())


# No está padre.
class NeighborhoodsRequest(BaseModel): 
    zipcode : str = Field(min_length=5, max_length=5)

# No está padre.
class MetaRequestNbhd(BaseModel): 
    neighborhoodsRequest : NeighborhoodsRequest

# No está padre
class Neighborhoods(CustomModel): 
    numberOfNeighborhoods  : int
    neighborhoodAttributes : List[str]
    neighborhoodsSet       : List[Neighborhood]

    @classmethod
    def from_df(cls, df):
        pre_neighborhoods = [Neighborhood(**nbhr_row) 
            for _, nbhr_row in df.iterrows()]
        new_obj = cls(
            numberOfNeighborhoods = len(pre_neighborhoods), 
            neighborhoodAttributes = list(Neighborhood.__fields__),
            neighborhoodsSet = pre_neighborhoods)
        return new_obj


# No está padre
class NeighborhoodsResponse(CustomModel): 
    zipcode       : Zipcode
    neighborhoods : Neighborhoods

    @classmethod
    def from_df(cls, df, first_zipcode=False):
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
