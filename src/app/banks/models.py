from typing import List, Optional

from pydantic import BaseModel


class Bank(BaseModel): 
    name        : str
    code        : Optional[str]
    banxicoId   : str
    alias       : str
    spei        : bool
    portability : bool

class BanksResponse(BaseModel): 
    numberOfBanks   : int
    bankAttributes  : List[str]
    banksSet        : List[Bank]

class BankAcquiring(BaseModel): 
    name  : str
    codeAcquiring : Optional[str]

class CardsBin(BaseModel): 
    bin       : str
    length    : int
    bankId    : str
    bank      : str
    banxicoId : str
    nature    : str
    brand     : str 

