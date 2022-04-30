from parsing_error import ParsingError
from abc import ABC


class MalformedICAPRequestError(ParsingError, ABC):
    pass


class MissingEncapsulatedHeaderError(MalformedICAPRequestError):
    def __init__(self):
        super().__init__(
            message_header='The "Encapsulated" header is missing in the request.',
            observed_value='(missing)',
            expected_value='(value)'
        )


class MultipleEncapsulatedHeadersError(MalformedICAPRequestError):
    def __init__(self, observed_num_headers: int):
        super().__init__(
            message_header='Multiple "Encapsulated" headers were observed in the request.',
            observed_value=observed_num_headers,
            expected_value=1
        )


class BadEncapsulatedEntityNameError(ParsingError):
    def __init__(self, observed_entity_name: bytes, expected_entity_names: list[bytes]):
        super().__init__(
            message_header=f'Bad encapsulated entity name.',
            observed_value=observed_entity_name,
            expected_label='Expected any of',
            expected_value=expected_entity_names
        )


class DuplicateEncapsulatedEntityNamesError(ParsingError):
    def __init__(self, duplicate_name: bytes):
        super().__init__(
            message_header=f'Duplicate encapsulated entity name.',
            observed_value=duplicate_name,
            expected_value=f'(single occurrence of {duplicate_name})'
        )


class EncapsulatedEntityOffsetIsNotIntegerError(ParsingError):
    def __init__(self, observed_value: bytes):
        super().__init__(
            message_header=f'The encapsulated entity offset is not an integer.',
            observed_value=observed_value,
            expected_value='(an integer)'
        )


class NegativeEncapsulatedEntityOffsetError(ParsingError):
    def __init__(self, observed_offset: int):
        super().__init__(
            message_header=f'The encapsulated entity offset is negative.',
            observed_value=observed_offset,
            expected_value='(a positive integer)'
        )


class NonIncreasingEncapsulatedEntityOffsetError(ParsingError):
    def __init__(self, observed_offset: int, previous_offset: int):
        super().__init__(
            message_header='The encapsulated entity offset is not increasing.',
            observed_value=observed_offset,
            expected_value=f'(an integer greater than {previous_offset})'
        )


class BadICAPMethodError(ParsingError):
    def __init__(self, observed_icap_method: bytes, expected_icap_methods: list[bytes]):
        super().__init__(
            message_header='Bad ICAP method',
            observed_value=observed_icap_method,
            expected_label='Expected any of',
            expected_value=expected_icap_methods
        )
