import sys
from fastapi import FastAPI
from json import loads
import uvicorn

from .models import (MetaRequestNbhd, NeighborhoodsResponse, 
    ORJSONResponse, BanksResponse, Bank, CardsBin)
from src import engine
from config import VERSION


debug = ("debug" in sys.argv)

app = FastAPI(title="Centralized catalogs.", version=VERSION, 
    description="Setup and query all-purpose catalogs.",
    openapi_tags=[
        { "name": "Zipcodes" },
        { "name": "Banks" }, 
        { "name": "Base", "description": "Verify base call and version." },
        { "name": "Legacy" }],
    root_path="data/docs/v1/catalogs",
    default_response_class=ORJSONResponse)
    

@app.get("/", tags=["Base"])
async def verify_base_endpoint():
    return {"App Running Version": VERSION}


@app.post("/zipcode-neighborhoods", 
    response_model=NeighborhoodsResponse, tags=["Legacy"])
async def post_zipcode_object(a_request: MetaRequestNbhd):
    an_input = loads(a_request.json())["neighborhoodsRequest"]
    return engine.zipcode_request(an_input)


@app.get("/zipcode-neighborhoods", 
    response_model=NeighborhoodsResponse, tags=["Legacy"])
async def get_zipcode_object(a_request: MetaRequestNbhd):
    an_input = loads(a_request.json())["neighborhoodsRequest"]
    b_response = engine.zipcode_request(an_input)
    return b_response


@app.get("/zipcode-neighborhoods/{zipcode}", 
    response_model=NeighborhoodsResponse, tags=["Zipcodes"])
async def preferred_zipcode_neighborhoods(zipcode: str):
    return engine.zipcode_request({"zipcode": zipcode})


@app.get("/national-banks", 
    response_model=BanksResponse, tags=["Banks"])
def list_all_banks(): 
    return engine.banks_request(server="fastapi")


@app.get("/national-banks/parse-clabe/{clabe_key}", 
    response_model=Bank, tags=["Banks"])
def get_bank_details_from_clabe(clabe_key: str): 
    return engine.clabe_parse(clabe_key)


@app.get("/national-banks/card-number/{card_number}", 
    response_model=CardsBin, tags=["Banks"])
def get_bank_details_from_card_number(card_number: str): 
    bin_bank = engine.card_number_parse(card_number)
    return bin_bank


if __name__ == "__main__":
    if debug: 
        uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)
    else: 
        uvicorn.run(app, port=80, host="0.0.0.0")



