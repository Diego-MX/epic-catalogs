
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Table, NVARCHAR, BIGINT,INT
from sqlalchemy.ext.declarative import declarative_base


# No está padre.
class NeighborhoodsRequest(BaseModel):
    zipcode : str = Field(min_length=5, max_length=5)

# No está padre.
class MetaRequestNbhd(BaseModel):
    neighborhoodsRequest : NeighborhoodsRequest



class Zipcode(BaseModel):
    zipcode    : str
    state      : str
    state_id   : str
    state_iso  : str
    borough    : str
    borough_id : str


class Neighborhood(BaseModel):
    zipcode : str = Field(min_length=5, max_length=5)
    name    : str
    zone    : str
    type    : str
    city    : Optional[str]
    city_id : Optional[str]


# No está padre
class Neighborhoods(BaseModel):
    numberOfNeighborhoods   : int
    neighborhoodAttributes  : List[str]
    neighborhoodsSet        : List[Neighborhood]


# No está padre
class NeighborhoodsResponse(BaseModel):
    zipcode       : Zipcode
    neighborhoods : Neighborhoods

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

# Finite incatatem

