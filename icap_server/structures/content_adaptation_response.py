from dataclasses import dataclass

from icap_server.structures.encapsulated_data import EncapsulatedData


@dataclass
class ContentAdaptationResponse:
    content: EncapsulatedData
    icap_response_code: int
    icap_response_headers: dict[bytes, list[bytes]]
    content_was_altered: bool
