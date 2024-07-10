
# pylint: disable=too-few-public-methods

from typing import List, Any, Optional

from fastapi.responses import JSONResponse
from orjson import dumps                
from pydantic import BaseModel, Field   



class ORJSONResponse(JSONResponse): 
    media_type = "application/json"

    def render(self, content: Any) -> bytes: 
        return dumps(content)


class NeighborhoodsRequest(BaseModel): 
    zipcode : str = Field(min_length=5, max_length=5)


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


class Neighborhoods(BaseModel): 
    numberOfNeighborhoods   : int
    neighborhoodAttributes  : List[str]
    neighborhoodsSet        : List[Neighborhood]


class NeighborhoodsResponse(BaseModel): 
    zipcode       : Zipcode
    neighborhoods : Neighborhoods


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
