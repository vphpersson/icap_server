from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from string import ascii_letters, digits
from random import choices as random_choices

from icap_server.structures.icap_status_line import ICAPStatusLine
from icap_server.structures.icap_response_body import ICAPResponseBody
from icap_server.structures.icap_method import ICAPMethod
from icap_server.structures.encapsulated_data import EncapsulatedData
from icap_server.structures.encapsulated_entity_name import EncapsulatedEntityName


@dataclass
class ICAPResponse:
    status_line: ICAPStatusLine
    header: Optional[bytes] = None
    body: Optional[ICAPResponseBody] = None

    @staticmethod
    def _build_header_bytes(headers_map: dict[bytes, list[bytes]]) -> bytes:

        header = bytearray()
        for header_name, header_values in headers_map.items():
            for header_value in header_values:
                header += (header_name + b': ' + header_value + b'\r\n')

        return bytes(header)

    def __bytes__(self) -> bytes:
        return bytes(self.status_line) + (self.header or b'') + b'\r\n' + (bytes(self.body) if self.body else b'')

    @classmethod
    def make(
        cls,
        method: ICAPMethod,
        encapsulated_data: EncapsulatedData,
        status_code: int,
        headers: dict[bytes, list[bytes]],
        add_required_headers: bool = True
    ) -> ICAPResponse:
        """

        :param method:
        :param encapsulated_data:
        :param status_code:
        :param headers:
        :param add_required_headers:
        :return:
        """

        if b'ISTag' not in headers and add_required_headers:
            headers[b'ISTag'] = [''.join(random_choices(population=(ascii_letters + digits), k=30)).encode()]

        if status_code != 204:
            match method:
                case ICAPMethod.REQMOD:
                    body_entity_name = EncapsulatedEntityName.REQBODY.value
                    header_entity_name = EncapsulatedEntityName.REQ_HDR.value

                    icap_response_body = ICAPResponseBody(
                        header=encapsulated_data.request_header,
                        encapsulated_body=encapsulated_data.request_body
                    )
                case ICAPMethod.RESPMOD:
                    body_entity_name = EncapsulatedEntityName.RESBODY.value
                    header_entity_name = EncapsulatedEntityName.RES_HDR.value

                    icap_response_body = ICAPResponseBody(
                        header=encapsulated_data.response_header,
                        encapsulated_body=encapsulated_data.response_body
                    )
                case ICAPMethod.OPTIONS:
                    body_entity_name = EncapsulatedEntityName.OPTBODY.value
                    header_entity_name = None

                    icap_response_body = ICAPResponseBody(
                        header=None,
                        encapsulated_body=encapsulated_data.options_body
                    )
                case _:
                    raise ValueError(...)
        else:
            body_entity_name = None
            header_entity_name = None
            icap_response_body = ICAPResponseBody()

        if b'Encapsulated' not in headers and add_required_headers:
            headers[b'Encapsulated'] = [
                icap_response_body.make_encapsulated_header(
                    body_entity_name=body_entity_name,
                    header_entity_name=header_entity_name
                )
            ]

        return ICAPResponse(
            status_line=ICAPStatusLine(status_code=status_code),
            header=cls._build_header_bytes(headers_map=headers),
            body=icap_response_body
        )



