
from fastapi import APIRouter

from . import engine, models

router = APIRouter(prefix='/zipcode-neighborhoods', tags=['ZipCodes'])


@router.get('/{zipcode}', 
        response_model=models.NeighborhoodsResponse)
async def preferred_zipcode_neighborhoods(zipcode: str):
    return engine.zipcode_request({'zipcode': zipcode})


@router.post('', tags=['Legacy'], 
        response_model=models.NeighborhoodsResponse)
async def post_zipcode_object(a_request: models.MetaRequestNbhd):
    an_input = a_request.neighborhoodsRequest
    return engine.zipcode_request(an_input)

