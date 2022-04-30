from asyncio import start_server, StreamReader, StreamWriter, run as asyncio_run
from typing import Optional, Awaitable, Callable, Any
from functools import partial
from contextlib import asynccontextmanager
from logging import getLogger

from icap_server.structures.icap_request import ICAPRequest
from icap_server.structures.encapsulated_data import EncapsulatedData
from icap_server.structures.icap_response import ICAPResponse
from icap_server.structures.icap_method import ICAPMethod
from icap_server.structures.content_adaptation_response import ContentAdaptationResponse

LOG = getLogger(__name__)


def check_if_connection_close(connection_header_values: Optional[list[bytes]]) -> bool:
    if connection_header_values is not None:
        if len(connection_header_values) != 1:
            raise ValueError(...)

        if next(iter(connection_header_values)) == 'close':
            return True

    return False


async def handle(
    reader: StreamReader,
    writer: StreamWriter,
    *,
    service_name_to_handler: dict[bytes, Callable[[ICAPRequest], Awaitable[ContentAdaptationResponse]]]
) -> None:

    while True:
        try:
            icap_request = await ICAPRequest.from_reader(reader=reader)
        except:
            # TODO: Handle specific exceptions?
            LOG.exception('An exception occurred when reading an ICAP request.')
            break

        if icap_request is None:
            break

        try:
            content_adaptation_response: ContentAdaptationResponse = await service_name_to_handler[icap_request.request_line.service_name](icap_request)
            icap_response_code: int = content_adaptation_response.icap_response_code

            # If the data is unmodified, try to avoid having to copy it back in the response to the client.
            if not content_adaptation_response.content_was_altered:
                if b'204' in icap_request.headers.get(b'allow', [b'']) or icap_request.headers.get(b'preview'):
                    icap_response_code = 204

            icap_response = ICAPResponse.make(
                method=icap_request.request_line.method,
                encapsulated_data=content_adaptation_response.content,
                status_code=icap_response_code,
                headers=content_adaptation_response.icap_response_headers
            )

            try:
                writer.write(data=bytes(icap_response))
                await writer.drain()
            except:
                LOG.exception('An exception occurred when writing an ICAP response.')
                continue

            LOG.info(f'"{bytes(icap_request.request_line).decode()}" {icap_response.status_line.status_code}')

            if check_if_connection_close(connection_header_values=icap_request.headers.get(b'connection')):
                break
        except:
            LOG.exception('Unexpected exception.')
            break

    # TODO: Write error response in case of problem,

    writer.close()

    try:
        await writer.wait_closed()
    except ConnectionResetError:
        pass


@asynccontextmanager
async def run_server(
    *,
    service_name_to_handler: dict[bytes, Callable[[ICAPRequest], Awaitable[ContentAdaptationResponse]]],
    server_options: Optional[dict[str, Any]] = None
) -> None:
    """

    :param service_name_to_handler: A map of handlers for ICAP service names.
    :param server_options: Options passed to `asyncio.start_server`.
    :return:
    """

    start_server_options = dict(
        client_connected_cb=partial(handle, service_name_to_handler=service_name_to_handler),
        **server_options
    )

    async with await start_server(**start_server_options) as server:
        yield server
