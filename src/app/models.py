
# pylint: disable=too-few-public-methods
from operator import attrgetter as α
from typing import Any

from fastapi.responses import JSONResponse
from orjson import dumps                
from pydantic import BaseModel
from toolz import compose, pipe
from toolz.curried import valmap as valmap_z

class ORJSONResponse(JSONResponse): 
    media_type = "application/json"
    def render(self, content:Any) -> bytes: 
        return dumps(content)


class CustomModel(BaseModel):
    """Esta clase surgió complicadamente.  
    Al utilizar 'alias' para leer la data, FastAPI convierte los campos en sus alias
    y entonces marcaba error.  
    Últimadamente no he podido deshacerme de los errores ResponseValidation, pero 
    sí me gustó dejar el EpicModel para centralizar algunos comportamientos. 
    """
    def to_dict(self):
        def to_original(data):
            if isinstance(data, BaseModel):
                original_dict = pipe(data.__fields__, 
                    valmap_z(compose(to_original, data.__getattr__, α('alias'))))
                return original_dict
            if isinstance(data, dict):
                return valmap_z(to_original)(data)
            if isinstance(data, list):
                return list(map(to_original, data))
            return data
        return to_original(self)

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {BaseModel: lambda v: v.to_dict()}
