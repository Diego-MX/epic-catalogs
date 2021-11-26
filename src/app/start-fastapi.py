from fastapi import FastAPI, Request
from json import loads
import uvicorn

from .models import MetaRequestNbhd, NeighborhoodsResponse
from src import engine



app = FastAPI(title="Catálogos centralizados de uso de las Apps.",
    version="1.0.13")


@app.get("/")
async def base_request():
    return {"App Running Version": "1.0.13"}


@app.post("/zipcode-neighborhoods", response_model=NeighborhoodsResponse)
async def zipcode_neighborhoods_req(a_request: MetaRequestNbhd):
    an_input = loads(a_request.json())["neighborhoodsRequest"]
    return engine.zipcode_request(an_input, server="fastapi")


@app.get("/zipcode-neighborhoods", response_model=NeighborhoodsResponse)
async def get_zipcode_neighborhoods_req(a_request: MetaRequestNbhd):
    an_input = loads(a_request.json())["neighborhoodsRequest"]
    return engine.zipcode_request(an_input, server="fastapi")

@app.get("/zipcode-neighborhoods/{zipcode}", response_model=NeighborhoodsResponse)
async def get_zipcode_neighborhoods_str(zipcode: str):
    return engine.zipcode_query(zipcode, server="fastapi")


@app.get("/national-banks")
def get_banks(): 
    return engine.banks_request(server="fastapi")


@app.post("/national-banks/parse-clabe/{clabe_key}")
def post_banks(clabe_key: str): 
    return engine.clabe_parse(clabe_key, server="fastapi")




if __name__ == "__main__":
    # uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)
    uvicorn.run(app, port=80, host="0.0.0.0")



