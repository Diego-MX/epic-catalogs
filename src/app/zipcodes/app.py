
from fastapi import APIRouter  #, encoders

from . import engine, models


router = APIRouter()

## Ya no jala... 🤷 
@router.post('', tags=['Legacy'], 
    response_model=models.NeighborhoodsResponse)
async def post_zipcode_object(meta_req: models.MetaRequestNbhd):
    return engine.zipcode_request(meta_req.neighborhoodsRequest.zipcode)
    

@router.get('/{zipcode}')
    # response_model=models.NeighborhoodsResponse
    # response_model_by_alias=False (es la idea, 
    #       pero no funciona para los atributos anidados)
async def preferred_zipcode_neighborhoods(zipcode:str):
    pre_response = engine.zipcode_request(zipcode)
    return pre_response # encoders.jsonable_encoder(pre_response)

