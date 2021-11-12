from flask import Flask, request

from src import engine, tools
import config 

SITE = config.SITE
app  = Flask(__name__)


@app.route("/", methods=["GET"])
def base_request():
    simple_dict = {"App Running Version":  "1.0.8"}
    return simple_dict


@app.route("/zipcode-neighborhoods", methods=["POST", "GET"])
def post_get_zipcode_neighborhoods():
    an_input = request.json

    input_file   = SITE/"refs/openapi/1-input-zipcode-nbhd.json"
    a_validation = tools.response_validate(an_input, input_file)

    if a_validation["error"]:
        return a_validation["output"]
    
    b_messages = engine.zipcode_request(an_input["neighborhoodsRequest"])
    return b_messages


@app.route("/national-banks", methods=["GET"])
def get_banks():    
    banks_response = engine.banks_request()
    return banks_response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)



