# Diego Villamil, EPIC
# CDMX, 1 de diciembre de 2021
"""Reads local Excel file, store as Feather, and uploads it to Blob Storage. 
"""
import os
import pandas as pd

from azure.identity import ClientSecretCredential 
from azure.storage.blob import BlobServiceClient

from .. import tools
from .. import SITE
from ...config import ENV_VARS


RUTA_WORDS = "product/epic-catalogs/app-services/offensive-words.feather"
mid_file = SITE/"refs/catalogs/offensive-words.feather"


words_lists = tools.read_excel_table(SITE/"refs/catalogs/api-catalogs.xlsx.lnk", 
    "offensive-words", "words_lists")

words_df = pd.DataFrame(columns=["Phrase", "Type"])
for wrd_ls in words_lists["nombre"].values:
    wrd_df = (tools.read_excel_table(SITE/"refs/catalogs/api-catalogs.xlsx.lnk", 
            "offensive-words", wrd_ls)
        .assign(Type = wrd_ls)
        .rename(columns = {"Frase": "Phrase"}))
    words_df = pd.concat([words_df, wrd_df], axis=0, ignore_index=True)

words_df.to_feather(mid_file)


# Y ahora subirlo a Lake Hylia. 

credential = ClientSecretCredential(**{k: os.getenv(v) 
        for (k, v) in ENV_VARS["app_sp"].items() })

blob_container = BlobServiceClient("https://lakehylia.blob.core.windows.net/", credential)

the_blob = blob_container.get_blob_client(container="bronze", blob=RUTA_WORDS)

with open(mid_file, "rb") as _local: 
    the_blob.upload_blob(_local)

