import os
from pathlib import Path

SITE = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())

VERSION = "1.0.21"


URLS = {
    "local-flask"   : "http://localhost:5000", 
    "local-fastapi" : "http://localhost:80", 
    "staging"       : "https://wap-prod-catalogs-dev.azurewebsites.net", 
    "qa"            : "https://apim-crosschannel-tech-dev.azure-api.net/data/catalogs/v1"
}

ENV_VARS = {
    "app_sp" : {
        "tenant_id"       : "AAD_TNT_ID",
        "subscription_id" : "AAD_SCTN_ID", 
        "client_id"       : "AAD_APP_ID", 
        "client_secret"   : "AAD_APP_SCT"}, 
}

DEFAULT_ENV = "staging"
