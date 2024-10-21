
# pylint: disable=too-few-public-methods
from typing import Any

from fastapi.responses import JSONResponse
from orjson import dumps                
from pydantic import BaseModel

class ORJSONResponse(JSONResponse): 
    media_type = "application/json"
    def render(self, content:Any) -> bytes: 
        return dumps(content)


class CustomModel(BaseModel):
    """Esta clase surgió complicadamente.  
    Al utilizar 'alias' para leer la data, FastAPI convierte los campos en sus alias
    y entonces marcaba error.  
    Últimadamente no he podido deshacerme de los errores ResponseValidation, pero 
    sí me gustó dejar el CustomModel para centralizar algunos comportamientos. 
    """
    def to_dict(self) -> dict:
        def to_original(data):
            if isinstance(data, BaseModel):
                aliased = {nn: to_original(getattr(data, ff.alias))
                    for nn, ff in data.__fields__.items()}
                return aliased
            if isinstance(data, dict):
                return {kk: to_original(vv) for kk, vv in data.items()}
            if isinstance(data, list):
                return [to_original(ll) for ll in data]
            return data
        return to_original(self)

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        json_encoders = {BaseModel: lambda v: v.to_dict()}
