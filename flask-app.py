import os
from pathlib import Path
from flask import Flask, request, jsonify

from src import engine 
from src import tools

SITE = Path(__file__).parent if '__file__' in globals() else Path(os.getcwd())
app  = Flask(__name__)


@app.route("/", methods=["GET"])
def show_base_request():
    simple_dict = {"App Running Version":  "1.0.5"}
    return simple_dict


@app.route("/v1/catalogs/get-zipcode-neighborhoods", methods=["POST", "GET"])
def get_from_zipcode():
    an_input = request.json

    input_file   = SITE/"refs"/"openapi"/"1-input-zipcode-nbhd.json"
    a_validation = tools.response_validate(an_input, input_file)

    try:
        if a_validation["error"]:
            return a_validation["output"]
        
        b_messages = engine.process_request(an_input["neighborhoodsRequest"])
        return b_messages
    
    except Exception as e:
        return (jsonify({"detail": str(e)}), 500)
      

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)



