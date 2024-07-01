"""Manage Azure Resources via a centralized object.
"""
# pylint: disable=missing-class-docstring

import os
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

import config


class AzureResourcer():
    def __init__(self, env: str, server=None): 
        self.env = env
        self.server = server
        self.config = config.ENV_VARS[env]
        self.set_credentials()

    def set_credentials(self): 
        if self.server == 'local':
            params = self.config['app_sp']
            self.credentials = ClientSecretCredential(**{k: os.getenv(v) 
                for (k, v) in params.items()})
        else: 
            self.credentials = DefaultAzureCredential()

    def get_blob_service(self):
        if not hasattr(self, 'credentials'): 
            self.set_credentials()

        params = self.config['storage']
        blob_serv = BlobServiceClient(params['url'], self.credentials)
        return blob_serv
