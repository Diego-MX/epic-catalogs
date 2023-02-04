from os import getcwd, environ
from pathlib import Path
from src.tools import dict_get
from dotenv import load_dotenv


SITE = Path(__file__).parent if '__file__' in globals() else Path(getcwd())

VERSION  = "1.0.49"

ENV      = dict_get(environ, ['ENV_TYPE', 'ENV'], 'wap')
SERVER   = environ.get('SERVER_TYPE', 'wap')
TEST_ENV = 'local'


URLS = {
    'local'     : 'http://localhost:80', 
    'staging'   : 'https://wap-prod-catalogs-dev.azurewebsites.net', 
    'qa'        : 'https://apim-crosschannel-tech-dev.azure-api.net/data/catalogs/v1'
}


ENV_VARS = {
    'dev' : {
        'storage' : {
            'url'   : 'https://lakehylia.blob.core.windows.net/'}, 
        'app_sp' : {
            'tenant_id'       : 'AAD_TNT_ID',
            'subscription_id' : 'AAD_SCTN_ID', 
            'client_id'       : 'AAD_APP_ID', 
            'client_secret'   : 'AAD_APP_SCT'} 
    }, 
    'qas' : {
        'storage' : {
            'url'   : 'https://stlakehyliaqas.blob.core.windows.net/'}
    }, 
    'stg' : {
        'storage' : {
            'url'   : 'https://stlakehyliastg.blob.core.windows.net/'}
    }, 
    'prd' : {
        'storage' : {
            'url'   : 'https://stlakehyliaprd.blob.core.windows.net/'}
    }, 
    'drp' : {
        'storage' : {
            'url'   : 'https://stlakehyliadrp.blob.core.windows.net/'}
    } 
}


