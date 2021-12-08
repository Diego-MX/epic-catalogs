
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from typing import List, Any, Optional
from orjson import dumps



# Fix bugs. 
class ORJSONResponse(JSONResponse): 
    media_type = "application/json"

    def render(self, content: Any) -> bytes: 
        return dumps(content)


# Request
class NeighborhoodsRequest(BaseModel): 
    zipcode : str = Field(min_length=5, max_length=5)

class MetaRequestNbhd(BaseModel): 
    neighborhoodsRequest : NeighborhoodsRequest


# Response
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
    name    : str
    code    : str
    warning : Optional[bool]

class BanksResponse(BaseModel): 
    numberOfBanks   : int
    bankAttributes  : List[str]
    banksSet        : List[Bank]

class CardsBin(BaseModel): 
    bin    : str
    length : int
    bankId : str
    bank   : str
    nature : str
    brand  : str 
