from datetime import date

from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from typing import List, Any, Optional, Tuple
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

class Pagination(BaseModel): 
    hasPagination  : bool
    # pages          : Tuple[int, int]
    # paginationURL  : Optional[str]
    # pageExpiration : Optional[date]

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
    neighborhoodsPagination : Optional[Pagination]

class NeighborhoodsResponse(BaseModel): 
    zipcode       : Zipcode
    neighborhoods : Neighborhoods



