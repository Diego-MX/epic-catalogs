
# pylint: disable=too-few-public-methods
from typing import List, Optional

from src.app.models import CustomModel


class Bank(CustomModel): 
    name        : str
    code        : Optional[str]
    banxicoId   : str
    alias       : str
    spei        : bool
    portability : bool

class BanksResponse(CustomModel): 
    numberOfBanks   : int
    bankAttributes  : List[str]
    banksSet        : List[Bank]

class BankAcquiring(CustomModel): 
    name  : str
    codeAcquiring : Optional[str]

class CardsBin(CustomModel): 
    bin       : str
    length    : int
    bankId    : str
    bank      : str
    banxicoId : str
    nature    : str
    brand     : str 

