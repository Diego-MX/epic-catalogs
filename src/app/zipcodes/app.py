
from fastapi import APIRouter

from . import engine, models

router = APIRouter(tags=['ZipCodes'])


## Ya no jala... 🤷 
@router.post('', tags=['Legacy'], 
        response_model=models.NeighborhoodsResponse)
async def post_zipcode_object(meta_req: models.MetaRequestNbhd):
    return engine.zipcode_request(meta_req.neighborhoodsRequest.zipcode)


@router.get('/{zipcode}', 
        response_model=models.NeighborhoodsResponse)
async def preferred_zipcode_neighborhoods(zipcode:str):
    return engine.zipcode_request(zipcode)

