import os
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from config import ENV_VARS



class AzureResourcer():
    def __init__(self, env: str): 
        self.env = env
        self.config = ENV_VARS[env]
        self.set_credentials()

    def set_credentials(self): 
        if self.env == 'local':
            params = self.config['app_sp']
            self.credentials = ClientSecretCredential(**{k: os.getenv(v) 
                for (k, v) in params.items()})
        if self.env in ['dev', 'qas', 'stg', 'prd']: 
            self.credentials = DefaultAzureCredential()

    def get_blob_service(self):
        params = self.config['storage']
        blob_serv = BlobServiceClient(params['url'], self.credentials)
        return blob_serv
