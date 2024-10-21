
from fastapi import APIRouter 

from . import engine, models


router = APIRouter()

## Ya no jala... 🤷 
# response_model=models.NeighborhoodsResponse
# response_model_by_alias=False (es la idea, 
#       pero no funciona para los atributos anidados)
@router.post('', tags=['Legacy']) 
async def post_zipcode_object(meta_req: models.MetaRequestNbhd):
    return engine.zipcode_request(meta_req.neighborhoodsRequest.zipcode)
    

@router.get('/{zipcode}')
async def preferred_zipcode_neighborhoods(zipcode:str):
    return engine.zipcode_request(zipcode)

