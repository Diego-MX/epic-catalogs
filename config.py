"""Set Azure Resources variables with Infra Team.
The purpose is to only define variables but don't run any code.
"""

VERSION  = "1.0.85"  # build_deploy.yml 

URLS = {
    'local'     : 'http://localhost:80', 
    'staging'   : 'https://wap-prod-catalogs-dev.azurewebsites.net', 
    'qa'        : 'https://apim-crosschannel-tech-dev.azure-api.net/data/catalogs/v1'}

ENV_VARS = {
    'dev' : {
        'app_sp' : {
            'tenant_id'       : 'AAD_TNT_ID_DEV',
            'subscription_id' : 'AAD_SCTN_ID_DEV', 
            'client_id'       : 'AAD_APP_ID_DEV', 
            'client_secret'   : 'AAD_APP_SCT_DEV'}, 
        'storage':  {'url': 'https://lakehylia.blob.core.windows.net/'} },
    'qas' : {
        'app_sp' : {
            'tenant_id'       : 'AAD_TNT_ID_QAS',
            'subscription_id' : 'AAD_SCTN_ID_QAS', 
            'client_id'       : 'AAD_APP_ID_QAS', 
            'client_secret'   : 'AAD_APP_SCT_QAS'}, 
        'storage':  {'url': 'https://lakehylia.blob.core.windows.net/'} },
} 


AZURE_VARS = {
    'dev': {
        'blob-storage': 'lakehylia'},
    'qas' : {  
        'blob-storage': 'stalakehyliaqas'}, 
    'stg' : {
        'blob-storage': 'stlakehyliastg'}, 
    'prd' : {
        'blob-storage': 'stlakehyliaprd'}, 
    'drp' : {
        'blob-storage': 'stlakehyliadrp'},
}