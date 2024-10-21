
# pylint: disable=too-few-public-methods
from typing import List

import numpy as np
import pandas as pd
from pydantic import Field

from sqlalchemy import Column, Table, NVARCHAR, BIGINT,INT
from sqlalchemy.ext.declarative import declarative_base

from src.app.models import CustomModel
from src.app.exceptions import ValidationError


### CustomModel

class Zipcode(CustomModel): 
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


### BaseModels

Base = declarative_base()

class CodigosDrive(Base):
    """Modelo ORM Codigos Drive"""
    __tablename__ = "codigos_drive"
    __table__ = Table('codigos_drive', Base.metadata,
                      Column("d_codigo",NVARCHAR),
                      Column("d_asenta",NVARCHAR),
                      Column("d_zona",NVARCHAR),
                      Column("c_estado",NVARCHAR),
                      Column("c_mnpio",NVARCHAR),
                      Column("c_cve_ciudad",NVARCHAR),
                      Column("c_tipo_asenta",NVARCHAR),
                      Column("id_tabla",BIGINT, primary_key=True))


class EstadosClaves(Base):
    """Modelo ORM estados_claves"""
    __tablename__ = "estados_claves"
    __table__ = Table("estados_claves", Base.metadata,
                    Column("clave",BIGINT,primary_key=True),
                    Column("nombre",NVARCHAR),
                    Column("ABR",NVARCHAR),
                    Column("Abr_1",NVARCHAR),
                    Column("ABR_2",NVARCHAR),
                    Column("renapo",NVARCHAR),
                    Column("ISO_3166",NVARCHAR),
                    Column("drive",NVARCHAR),
                    Column("gobmx",NVARCHAR),
                    Column("marco_geo",NVARCHAR),
                    Column("min_cp",BIGINT),
                    Column("max_cp",BIGINT),
                    Column("clave_2",BIGINT))


class CodigosDriveTipoAsentamientos(Base):
    """Modelo ORM codigos_drive_tipo_asentamientos"""

    __tablename__ = "codigos_drive_tipo_asentamientos"
    __table__ = Table("codigos_drive_tipo_asentamientos", Base.metadata,
                      Column("c_tipo_asenta",NVARCHAR, primary_key=True),
                      Column("d_tipo_asenta",NVARCHAR),
                      Column("n_asenta" ,INT))


class CodigosDriveMunicipios(Base):
    """Modelo ORM codigos_drive_municipios"""

    __tablename__ = "codigos_drive_municipios"
    __table__ = Table("codigos_drive_municipios", Base.metadata,
                      Column("c_estado",NVARCHAR),
                      Column("c_mnpio",NVARCHAR),
                      Column("d_mnpio",NVARCHAR),
                      Column("min_cp",NVARCHAR),
                      Column("max_cp",NVARCHAR),
                      Column("id_tabla",BIGINT,primary_key=True))


class CodigosDriveCiudades(Base):
    """Modelo ORM codigos_drive_ciudades"""

    __tablename__ = "codigos_drive_ciudades"
    __table__ = Table("codigos_drive_ciudades", Base.metadata,
                      Column("c_estado",NVARCHAR),
                      Column("c_cve_ciudad",NVARCHAR),
                      Column("d_ciudad",NVARCHAR),
                      Column("id_tabla",BIGINT,primary_key=True))


### Legacy Model:  horrrribles. 
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
    def from_df(cls, a_df:pd.DataFrame) -> 'Neighborhoods':
        the_obj = cls(
            numberOfNeighborhoods = a_df.shape[0], 
            neighborhoodAttributes = list(Neighborhood.__fields__),
            neighborhoodsSet = [Neighborhood.from_orm(nn) 
                for nn in a_df.itertuples()])
        return the_obj


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
            zipcode = Zipcode.from_orm(df.loc[0, zip_cols]), 
            neighborhoods = Neighborhoods.from_df(df))
        return the_object


