from enum import Enum
from typing import List, Optional, Type

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


class CardNumberCall(Enum): 
    BANK = 'bank'
    BIN = 'bin'

    @property
    def model_class(self) -> Type[BaseModel]:
        model_map = {
            "bank": Bank,
            "bin": CardsBin}
        return model_map[self.value]
