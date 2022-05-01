from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import ParseResultBytes, urlparse
from typing import ClassVar
from re import Pattern as RePattern, compile as re_compile

from icap_server.structures.icap_method import ICAPMethod
from icap_server.exceptions import BadICAPMethodError, MalformedICAPRequestLine


@dataclass
class ICAPRequestLine:
    method: ICAPMethod
    uri: ParseResultBytes
    version_string: bytes

    _REQUEST_LINE_PATTERN: ClassVar[RePattern] = re_compile(
        pattern=b'^(?P<method>[^ ]+) (?P<uri>icap://[^ ]+) ICAP/(?P<version_string>\d+\.\d+)$'
    )

    @property
    def version(self) -> tuple[int, int]:
        pair: list[bytes] = self.version_string.split(sep=b'.', maxsplit=1)
        return int(pair[0]), int(pair[1])

    @property
    def service_name(self) -> bytes:
        return self.uri.path.removeprefix(b'/')

    def __bytes__(self) -> bytes:
        return self.method.value + b' ' + self.uri.geturl() + b' ICAP/' + self.version_string

    @classmethod
    def from_bytes(cls, data: bytes) -> ICAPRequestLine:

        if (match := cls._REQUEST_LINE_PATTERN.match(string=data.rstrip())) is None:
            raise MalformedICAPRequestLine(observed_request_line=data)
        else:
            group_dict = match.groupdict()
            method_bytes: bytes = group_dict['method']

            try:
                method = ICAPMethod(group_dict['method'])
            except ValueError as e:
                raise BadICAPMethodError(
                    observed_icap_method=method_bytes,
                    expected_icap_methods=list(ICAPMethod)
                ) from e

            return cls(
                method=method,
                uri=urlparse(url=group_dict['uri']),
                version_string=group_dict['version_string']
            )
