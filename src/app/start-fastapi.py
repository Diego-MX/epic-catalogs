from fastapi import FastAPI, Request
from json import loads
import uvicorn

from .models import MetaRequestNbhd, NeighborhoodsResponse
from src import engine



app = FastAPI(title="Catálogos centralizados de uso de las Apps.",
    version="1.0.12")


@app.get("/")
async def base_request():
    simple_dict = {"App Running Version": "1.0.12"}
    return simple_dict


@app.post("/zipcode-neighborhoods", response_model=NeighborhoodsResponse)
async def post_zipcode_neighborhoods_req(a_request: MetaRequestNbhd):
    an_input = loads(a_request.json())["neighborhoodsRequest"]

    b_messages = engine.zipcode_request(an_input, server="fastapi")
    return b_messages


@app.get("/zipcode-neighborhoods", response_model=NeighborhoodsResponse)
async def get_zipcode_neighborhoods_req(a_request: MetaRequestNbhd):
    an_input = loads(a_request.json())["neighborhoodsRequest"]

    b_messages = engine.zipcode_request(an_input, server="fastapi")
    return b_messages

@app.get("/zipcode-neighborhoods/{zipcode}", response_model=NeighborhoodsResponse)
async def get_zipcode_neighborhoods_str(zipcode: str):
    b_messages = engine.zipcode_query(zipcode, server="fastapi")
    return b_messages


@app.get("/national-banks")
def get_banks(): 
    banks_response = engine.banks_request(server="fastapi")
    return banks_response



if __name__ == "__main__":
    # uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)
    uvicorn.run(app, port=80, host="0.0.0.0")



