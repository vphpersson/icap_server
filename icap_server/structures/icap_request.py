from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from asyncio import StreamReader
from itertools import zip_longest
from collections import defaultdict

from icap_server.structures.icap_request_line import ICAPRequestLine
from icap_server.structures.encapsulated_data import EncapsulatedData
from icap_server.structures.encapsulated_entity_name import EncapsulatedEntityName
from icap_server.structures.icap_method import ICAPMethod
from icap_server.exceptions import MissingEncapsulatedHeaderError, MultipleEncapsulatedHeadersError, \
    BadEncapsulatedEntityNameError, DuplicateEncapsulatedEntityNamesError, EncapsulatedEntityOffsetIsNotIntegerError, \
    NegativeEncapsulatedEntityOffsetError, NonIncreasingEncapsulatedEntityOffsetError


@dataclass
class ICAPRequest:
    request_line: ICAPRequestLine
    headers: dict[bytes, list[bytes]]
    body: EncapsulatedData

    @staticmethod
    def _parse_encapsulated_header(
        encapsulated_header_values: Optional[list[bytes]],
        method: ICAPMethod
    ) -> dict[EncapsulatedEntityName, int]:
        """
        Parse the ICAP `Encapsulated` header.

        :param encapsulated_header_values:
        :param method:
        :return:
        """

        if encapsulated_header_values is None:
            if method in {ICAPMethod.REQMOD, ICAPMethod.RESPMOD}:
                raise MissingEncapsulatedHeaderError()

            return {}

        if (num_headers_observed := len(encapsulated_header_values)) != 1:
            raise MultipleEncapsulatedHeadersError(observed_num_headers=num_headers_observed)

        encapsulated_header_value: bytes = next(iter(encapsulated_header_values))
        name_to_offset: dict[EncapsulatedEntityName, int] = {}

        previous_offset: int = -1
        for encapsulated_entity in encapsulated_header_value.split(sep=b', '):
            name_bytes: bytes
            value_bytes: bytes

            name_bytes, value_bytes = encapsulated_entity.split(sep=b'=', maxsplit=1)

            try:
                encapsulated_entity_name = EncapsulatedEntityName(value=name_bytes)
            except ValueError as e:
                raise BadEncapsulatedEntityNameError(
                    observed_entity_name=value_bytes,
                    expected_entity_names=list(EncapsulatedEntityName)
                ) from e

            if encapsulated_entity_name in name_to_offset:
                raise DuplicateEncapsulatedEntityNamesError(duplicate_name=encapsulated_entity_name.value)

            # TODO: Check if `encapsulated_entity_name` is allowed with method.

            try:
                value_int = int(value_bytes)
            except ValueError as e:
                raise EncapsulatedEntityOffsetIsNotIntegerError(observed_value=value_bytes) from e

            if not (value_int >= 0):
                raise NegativeEncapsulatedEntityOffsetError(observed_offset=value_int)

            if not (value_int > previous_offset):
                raise NonIncreasingEncapsulatedEntityOffsetError(
                    observed_offset=value_int,
                    previous_offset=previous_offset
                )

            previous_offset = value_int

            name_to_offset[encapsulated_entity_name] = value_int

        # TODO: Check if order is correct.

        return name_to_offset

    @staticmethod
    async def _read_encapsulated_data(reader: StreamReader, method: ICAPMethod, encapsulated_header_values: Optional[list[bytes]]) -> EncapsulatedData:

        encapsulated_entity_name_to_offset: dict[EncapsulatedEntityName, int] = ICAPRequest._parse_encapsulated_header(
            encapsulated_header_values=encapsulated_header_values,
            method=method
        )

        entries: list[tuple[EncapsulatedEntityName, bytes]] = []

        bytes_read = 0
        for entity_name, offset in zip_longest(encapsulated_entity_name_to_offset.keys(), list(encapsulated_entity_name_to_offset.values())[1:], fillvalue=None):
            if entity_name is EncapsulatedEntityName.NULLBODY:
                continue

            if offset is None:
                chunks_data = bytearray()
                while True:
                    chunk_line = await reader.readline()
                    if not chunk_line:
                        break

                    chunk_line_arr = chunk_line.split(sep=b';', maxsplit=1)
                    bytes_to_read = int(chunk_line_arr[0], 16)

                    chunk_data = await reader.readexactly(bytes_to_read)
                    await reader.readexactly(2)

                    if chunk_data == b'':
                        break

                    chunks_data += chunk_data

                if chunks_data:
                    entries.append((entity_name, bytes(chunks_data)))
            else:
                bytes_to_read = offset - bytes_read
                bytes_read += bytes_to_read

                entries.append((entity_name, (await reader.readexactly(bytes_to_read - 2))))
                await reader.readexactly(2)

        return EncapsulatedData.from_entries(entries=entries)

    @staticmethod
    async def _read_icap_headers(reader: StreamReader) -> dict[bytes, list[bytes]]:
        """
        Read header name and values from a reader.

        :param reader: A reader from which to read header lines.
        :return: ICAP headers as a `dict`.
        """

        headers: dict[bytes, list[bytes]] = defaultdict(list)

        # TODO: Add timeout?
        header_line_bytes: bytes
        while header_line_bytes := (await reader.readline()).rstrip():
            name: bytes
            value: bytes

            name, value = header_line_bytes.split(sep=b': ', maxsplit=1)
            headers[name.lower()].append(value)

        return dict(headers)

    # TODO: Add timeout parameter?
    @classmethod
    async def from_reader(cls, reader: StreamReader) -> Optional[ICAPRequest]:

        request_line_bytes = await reader.readline()
        if not request_line_bytes:
            return None

        request_line = ICAPRequestLine.from_bytes(data=request_line_bytes)
        headers: dict[bytes, list[bytes]] = await cls._read_icap_headers(reader=reader)

        return cls(
            request_line=request_line,
            headers=headers,
            body=await cls._read_encapsulated_data(
                reader=reader,
                method=request_line.method,
                encapsulated_header_values=headers.get(b'encapsulated')
            )
        )
