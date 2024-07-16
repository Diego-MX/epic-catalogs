
from fastapi import FastAPI
import uvicorn

from src.app import models
from config import VERSION

from . import debug_mode, root_path, banks, zipcodes, models


app = FastAPI(title='Centralized catalogs.', version=VERSION, 
    description='Setup and query all-purpose catalogs.',
    openapi_tags=[{'name': 'Base', 'description': 'Verify base call and version.'}],
        #{'name': 'Zipcodes'},{'name': 'Banks'},{'name': 'Legacy'}],
    root_path=root_path,
    default_response_class=models.ORJSONResponse)

@app.get('/', tags=['Base'])
async def verify_base_endpoint():
    return {'App Running Version': VERSION}

app.include_router(zipcodes.calls.router)
app.include_router(banks.calls.router)


if __name__ == '__main__': 
    if debug_mode: 
        uvicorn.run('__main__:app', port=80, host='0.0.0.0', reload=True)
    else: 
        uvicorn.run(app, port=80, host='0.0.0.0')

