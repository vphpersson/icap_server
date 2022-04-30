from enum import Enum


class ICAPMethod(Enum):
    OPTIONS = b'OPTIONS'
    REQMOD = b'REQMOD'
    RESPMOD = b'RESPMOD'
