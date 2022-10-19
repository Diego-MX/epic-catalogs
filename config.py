from os import getcwd, environ
from pathlib import Path
from src.tools import dict_get

SITE = Path(__file__).parent if '__file__' in globals() else Path(getcwd())

VERSION  = "1.0.38"

ENV      = dict_get(environ, ['ENV_TYPE', 'ENV'], 'wap')
SERVER   = environ.get('SERVER_TYPE', 'wap')
TEST_ENV = 'local'


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


