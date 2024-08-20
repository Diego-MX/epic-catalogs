"""
Modelos de bancos provenientes de FASTAPI y SQLALCHEMY
"""

from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, BIGINT, NVARCHAR, INT, Table, DATETIME
from sqlalchemy.ext.declarative import declarative_base

class Bank(BaseModel):
    name        : str
    code        : Optional[str]
    banxicoId   : str
    alias       : str
    spei        : bool
    portability : bool

class BanksResponse(BaseModel):
    numberOfBanks   : int
    bankAttributes  : List[str]
    banksSet        : List[Bank]

class BankAcquiring(BaseModel):
    name  : str
    codeAcquiring : Optional[str]

class CardsBin(BaseModel):
    bin       : str
    length    : int
    bankId    : str
    bank      : str
    banxicoId : str
    nature    : str
    brand     : str

Base = declarative_base()

class NationalBanksAcquiring(Base):
    """Modelo ORM NationalBanksAcquiring"""
    __tablename__ = "national_banks_acquiring"
    __table__ = Table("national_banks_acquiring", Base.metadata,
                      Column("tabla_id",BIGINT, primary_key=True),
                      Column("Institución",NVARCHAR),
                      Column("Cámara",NVARCHAR),
                      Column("ID Adquirente",NVARCHAR),
                      Column("Fecha de Alta",DATETIME))


class NationalBanksBins(Base):
    """Modelo ORM NationalBanksBins"""

    __tablename__ = "national_banks_bins"
    __table__ = Table("national_banks_bins", Base.metadata,
                    Column("BIN",BIGINT, primary_key=True),
                    Column("Rango",INT),
                    Column("Id Institución",INT),
                    Column("Institución",NVARCHAR),
                    Column("Producto",NVARCHAR),
                    Column("Naturaleza",NVARCHAR),
                    Column("Marca",NVARCHAR),
                    Column("Fecha de Alta",DATETIME),
                    Column("Procesador",NVARCHAR),
                    Column("banxico_id",NVARCHAR),
                    Column("ID",NVARCHAR))


class NationalBanks(Base):
    """Modelo ORM NationalBanks"""

    __tablename__ = "national_banks"
    __table__ = Table("national_banks", Base.metadata,
                    Column("index",NVARCHAR, primary_key=True),
                    Column("name" ,NVARCHAR),
                    Column("code" ,NVARCHAR),
                    Column("banxico_id",NVARCHAR),
                    Column("alias",NVARCHAR),
                    Column("spei" ,NVARCHAR),
                    Column("portability",NVARCHAR))

# Finite Incantatem
