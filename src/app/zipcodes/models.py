
from typing import List, Optional
from pydantic import BaseModel, Field


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
