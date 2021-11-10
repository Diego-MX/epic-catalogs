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
def get_from_zipcode():
    an_input = request.json

    input_file   = SITE/"refs/openapi/1-input-zipcode-nbhd.json"
    a_validation = tools.response_validate(an_input, input_file)

    if a_validation["error"]:
        return a_validation["output"]
    
    b_messages = engine.process_request(an_input["neighborhoodsRequest"])
    return b_messages


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)



