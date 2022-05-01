from dataclasses import dataclass, InitVar
from typing import Optional

from icap_server.structures.encapsulated_entity_name import EncapsulatedEntityName
from icap_server.exceptions import HeaderValueButMissingHeaderEntityNameError


@dataclass
class ICAPResponseBody:
    header: Optional[bytes] = None
    body: Optional[bytes] = None
    encapsulated_body: InitVar[bytes] = None

    def __post_init__(self, encapsulated_body: Optional[bytes]):
        if self.body is None and encapsulated_body:
            self.body = f'{len(encapsulated_body):x}'.encode() + b'\r\n' + encapsulated_body + b'\r\n' + b'0\r\n\r\n'

    def __bytes__(self) -> bytes:
        return (
            ((self.header + b'\r\n') if self.header else b'') + (self.body or b'')
        )

    def make_encapsulated_header(self, body_entity_name: Optional[bytes] = None, header_entity_name: Optional[bytes] = None) -> bytes:
        body_entity_name: bytes = body_entity_name if self.body else EncapsulatedEntityName.NULLBODY.value

        if self.header:
            if header_entity_name is None:
                raise HeaderValueButMissingHeaderEntityNameError

            return header_entity_name + b'=0, ' + body_entity_name + b'=' + str(len(self.header)).encode()
        else:
            return body_entity_name + b'=0'
