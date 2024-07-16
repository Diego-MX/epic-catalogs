
from json import loads
from fastapi import APIRouter, HTTPException

from . import engine, models

router = APIRouter(prefix='/zipcode-neighborhoods', tags=['ZipCodes'])


@router.get('/{zipcode}', 
        response_model=models.NeighborhoodsResponse)
async def preferred_zipcode_neighborhoods(zipcode: str):
    try: 
        return engine.zipcode_request({'zipcode': zipcode})
    except Exception as exc: 
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post('', tags=['Legacy'], 
        response_model=models.NeighborhoodsResponse)
async def post_zipcode_object(a_request: models.MetaRequestNbhd):
    an_input = loads(a_request.json())['neighborhoodsRequest']
    return engine.zipcode_request(an_input)


@router.get('', tags=['Legacy'], 
        response_model=models.NeighborhoodsResponse)
async def get_zipcode_object(a_request: models.MetaRequestNbhd):
    an_input = loads(a_request.json())['neighborhoodsRequest']
    return engine.zipcode_request(an_input)

