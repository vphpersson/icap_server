#!/usr/bin/env python

from typing import Final, Type, NoReturn
from collections import defaultdict
from asyncio.base_events import Server
from asyncio import run as asyncio_run
from logging import getLogger, Logger, INFO, StreamHandler, ERROR
from sys import stderr, stdout

from ecs_tools_py import make_log_handler

from icap_server.structures.icap_request import ICAPRequest
from icap_server.structures.content_adaptation_response import ContentAdaptationResponse
from icap_server.structures.icap_method import ICAPMethod
from icap_server.exceptions import UnexpectedCase
from icap_server.cli import ICAPServerArgumentParser
from icap_server import run_server


LOG: Final[Logger] = getLogger(__name__)


async def service_handler(icap_request: ICAPRequest) -> ContentAdaptationResponse:
    """
    Handle an incoming ICAP request that is available for content adaptation.

    :param icap_request: An ICAP request available for content adaptation.
    :return: Information about the content adaptation performed.
    """

    icap_response_headers: dict[bytes, list[bytes]] = defaultdict(list)

    if request_header := icap_request.body.request_header:
        LOG.info(request_header.split(sep=b'\n', maxsplit=1)[0].rstrip().decode())

    match method := icap_request.request_line.method:
        case ICAPMethod.OPTIONS:
            icap_response_code = 200
            icap_response_headers[b'Methods'].append(b'REQMOD')
            icap_response_headers[b'Preview'].append(b'0')
        case ICAPMethod.REQMOD:
            icap_response_code = 200
        case _:
            raise UnexpectedCase(observed_case=method, expected_cases=[ICAPMethod.OPTIONS, ICAPMethod.REQMOD])

    return ContentAdaptationResponse(
        content=icap_request.body,
        icap_response_code=icap_response_code,
        icap_response_headers=dict(icap_response_headers),
        content_was_altered=False
    )


async def main() -> NoReturn:
    from icap_server import LOG as ICAP_SERVER_LOG
    from ecs_tools_py.system import LOG as ECS_TOOLS_PY_SYSTEM_LOG

    ICAP_SERVER_LOG.setLevel(level=ERROR)
    ICAP_SERVER_LOG.addHandler(hdlr=make_log_handler(StreamHandler)(stream=stderr))
    ECS_TOOLS_PY_SYSTEM_LOG.setLevel(level=ERROR)
    ECS_TOOLS_PY_SYSTEM_LOG.addHandler(hdlr=make_log_handler(StreamHandler)(stream=stderr))

    LOG.setLevel(level=INFO)
    LOG.addHandler(hdlr=StreamHandler(stream=stdout))

    args: Type[ICAPServerArgumentParser.Namespace] = ICAPServerArgumentParser().parse_args()

    run_server_options = dict(
        service_name_to_handler={args.service_name.encode(): service_handler},
        server_options=dict(host=args.host, port=args.port)
    )

    server: Server
    async with run_server(**run_server_options) as server:
        LOG.info(f'Starting ICAP server on {args.host}:{args.port} with service \"{args.service_name}\".')
        await server.serve_forever()


if __name__ == '__main__':
    asyncio_run(main())
