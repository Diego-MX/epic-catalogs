
# pylint: disable=too-few-public-methods
from typing import Any

from fastapi.responses import JSONResponse
from orjson import dumps                

class ORJSONResponse(JSONResponse): 
    media_type = "application/json"
    def render(self, content:Any) -> bytes: 
        return dumps(content)
