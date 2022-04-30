from enum import Enum


class EncapsulatedEntityName(Enum):
    REQ_HDR = b'req-hdr'
    RES_HDR = b'res-hdr'
    REQBODY = b'req-body'
    RESBODY = b'res-body'
    OPTBODY = b'opt-body'
    NULLBODY = b'null-body'
