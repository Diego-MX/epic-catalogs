"""
__init__.py

Programa
Se obtienen las varibles de ambiente y se ajusta la ruta de uso
"""

from os import getcwd, getenv
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(override=True)

ENV = getenv('ENV_TYPE')
SERVER   = getenv('SERVER_TYPE')

SITE = Path(__file__).parents[1] if '__file__' in globals() else Path(getcwd())
