import os
from pathlib import Path

SITE = Path(__file__).parent if '__file__' in globals() else Path(os.getcwd())

VERSION = "1.0.33"

ENV  = os.environ.get('ENV', 'local')  # local, dev, qas, databricks

URLS = {
    'local'     : 'http://localhost:80', 
    'staging'   : 'https://wap-prod-catalogs-dev.azurewebsites.net', 
    'qa'        : 'https://apim-crosschannel-tech-dev.azure-api.net/data/catalogs/v1'
}

ENV_VARS = {
    'local' : {
        'app_sp' : {
            'tenant_id'       : 'AAD_TNT_ID',
            'subscription_id' : 'AAD_SCTN_ID', 
            'client_id'       : 'AAD_APP_ID', 
            'client_secret'   : 'AAD_APP_SCT'},
        'storage' : {
            'url'   : 'https://lakehylia.blob.core.windows.net/'}
    }, 
    'dev' : {
        'storage' : {
            'url'   : 'https://lakehylia.blob.core.windows.net/'}
    }, 
    'qas' : {
        'storage' : {
            'url'   : 'https://stlakehylia.blob.core.windows.net/'}
    } 
}


