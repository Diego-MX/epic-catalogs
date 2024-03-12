from os import getcwd, environ
from pathlib import Path
from src.tools import dict_get


SITE = Path(__file__).parent if '__file__' in globals() else Path(getcwd())

VERSION  = "1.0.71"  # build_deploy.yml 

ENV      = dict_get(environ, ['ENV_TYPE', 'ENV'])
SERVER   = environ.get('SERVER_TYPE', 'wap')
TEST_ENV = 'local'


URLS = {
    'local'     : 'http://localhost:80', 
    'staging'   : 'https://wap-prod-catalogs-dev.azurewebsites.net', 
    'qa'        : 'https://apim-crosschannel-tech-dev.azure-api.net/data/catalogs/v1'
}


ENV_VARS = {
    'dev' : {
        'app_sp' : {
            'tenant_id'       : 'AAD_TNT_ID',
            'subscription_id' : 'AAD_SCTN_ID', 
            'client_id'       : 'AAD_APP_ID', 
            'client_secret'   : 'AAD_APP_SCT'}, 
        'storage':  {'url': 'https://lakehylia.blob.core.windows.net/'}, 
    }, 
}


AZURE_VARS = {
    'dev': {
        'blob-storage': 'lakehylia'},
    'qas' : {  # url: 'https://{}.blob.core.windows.net/'
        'blob-storage': 'stalakehyliaqas'}, 
    'stg' : {
        'blob-storage': 'stlakehyliastg'}, 
    'prd' : {
        'blob-storage': 'stlakehyliaprd'}, 
    'drp' : {
        'blob-storage': 'stlakehyliadrp'},
}