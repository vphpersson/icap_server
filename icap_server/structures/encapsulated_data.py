from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable

from icap_server.structures.encapsulated_entity_name import EncapsulatedEntityName


@dataclass
class EncapsulatedData:
    request_header: Optional[bytes] = None
    response_header: Optional[bytes] = None
    request_body: Optional[bytes] = None
    response_body: Optional[bytes] = None
    options_body: Optional[bytes] = None

    @classmethod
    def from_entries(cls, entries: Iterable[tuple[EncapsulatedEntityName, bytes]]) -> EncapsulatedData:

        kwargs: dict[str, bytes] = {}

        for key, value in entries:
            match key:
                case EncapsulatedEntityName.REQ_HDR:
                    kwargs['request_header'] = value
                case EncapsulatedEntityName.RES_HDR:
                    kwargs['response_header'] = value
                case EncapsulatedEntityName.REQBODY:
                    kwargs['request_body'] = value
                case EncapsulatedEntityName.RESBODY:
                    kwargs['response_body'] = value
                case EncapsulatedEntityName.OPTBODY:
                    kwargs['options_body'] = value
                case _:
                    raise ValueError(...)

        return cls(**kwargs)
