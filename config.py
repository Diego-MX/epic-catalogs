import os
from pathlib import Path

SITE = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())

DEFAULT_ENV = "staging"

URLS = {
    "local-flask"   : "http://localhost:5000", 
    "local-fastapi" : "http://localhost:80", 
    "staging"       : "https://wap-prod-catalogs-dev.azurewebsites.net", 
    "qa"            : "https://apim-crosschannel-tech-dev.azure-api.net/data/catalogs/v1"
}

ENV_VARS = {
    ""
}
