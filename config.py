import os
from pathlib import Path

SITE = Path(__file__) if "__file__" in globals() else Path(os.getcwd())

DEFAULT_ENV = "staging"

ENV_URLS = {
    "local"     : "http://localhost:5000", 
    "staging"   : "https://wap-prod-catalogs-dev.azurewebsites.net", 
    "qa"        : "https://apim-crosschannel-tech-dev.azure-api.net/data/catalogs/zipcode-neighborhoods"
}
