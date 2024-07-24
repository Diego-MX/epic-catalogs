<<<<<<< HEAD
"""
    Models
su importancia radica en la forma en que se manipulan los datos,
para ser enviados y recibidos
"""

from typing import List, Any, Optional

from fastapi.responses import JSONResponse
from orjson import dumps                # pylint: disable=no-name-in-module
from pydantic import BaseModel, Field   # pylint: disable=no-name-in-module
=======
>>>>>>> dev-diego

# pylint: disable=too-few-public-methods
from typing import Any

from fastapi.responses import JSONResponse
from orjson import dumps                

class ORJSONResponse(JSONResponse):
    media_type = "application/json"
    def render(self, content: Any) -> bytes: 
        return dumps(content)
