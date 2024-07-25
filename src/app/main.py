
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from config import VERSION

from . import debug_mode, root_path
from . import models as main_models
from .exceptions import CatalogsError
from .zipcodes.app import router as zipcodes_router
from .banks.app import router as banks_router


app = FastAPI(title='Centralized catalogs.', version=VERSION, 
    description='Setup and query all-purpose catalogs.',
    openapi_tags=[
        {'name': 'Zipcodes'},
        {'name': 'Banks'},
        {'name': 'Base', 'description': 'Verify base call and version.'}],
    root_path=root_path,
    default_response_class=main_models.ORJSONResponse)


@app.exception_handler(CatalogsError)
async def catalogs_exception_handler(_:Request, exc:CatalogsError):
    exc_code = CatalogsError.mapping.get(type(exc), 500)
    exc_response = JSONResponse(
        status_code=exc_code,
        content={"message": f"{exc.name}: {exc.detail}"})
    return exc_response

@app.get('/', tags=['Base'])
async def verify_base_endpoint():
    return {'App Running Version': VERSION}

app.include_router(zipcodes_router, 
    prefix='/zipcode-neighborhoods', 
    tags=['Zipcodes'])

app.include_router(banks_router, 
    prefix='/national-banks', 
    tags=['Banks'])


if __name__ == '__main__': 
    if debug_mode: 
        uvicorn.run('__main__:app', port=80, host='0.0.0.0', reload=True)
    else:
        uvicorn.run(app, port=80, host='0.0.0.0')
