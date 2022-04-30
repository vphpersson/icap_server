from dataclasses import dataclass
from typing import Optional, ClassVar


@dataclass
class ICAPStatusLine:
    status_code: int
    reason_phrase: Optional[bytes] = None

    STATUS_CODE_MAP: ClassVar[dict[int, tuple[str, ...]]] = {
        100: (b'Continue', b'Request received, please continue'),
        101: (b'Switching Protocols', b'Switching to new protocol; obey Upgrade header'),
        200: (b'OK', b'Request fulfilled, document follows'),
        201: (b'Created', b'Document created, URL follows'),
        202: (b'Accepted', b'Request accepted, processing continues off-line'),
        203: (b'Non-Authoritative Information', b'Request fulfilled from cache'),
        204: (b'No Content', b'Request fulfilled, nothing follows'),
        205: (b'Reset Content', b'Clear input form for further input.'),
        206: (b'Partial Content', b'Partial content follows.'),
        300: (b'Multiple Choices', b'Object has several resources -- see URI list'),
        301: (b'Moved Permanently', b'Object moved permanently -- see URI list'),
        302: (b'Found', b'Object moved temporarily -- see URI list'),
        303: (b'See Other', b'Object moved -- see Method and URL list'),
        304: (b'Not Modified', b'Document has not changed since given time'),
        305: (b'Use Proxy', b'You must use proxy specified in Location to access this resource.'),
        307: (b'Temporary Redirect', b'Object moved temporarily -- see URI list'),
        400: (b'Bad Request', b'Bad request syntax or unsupported method'),
        401: (b'Unauthorized', b'No permission -- see authorization schemes'),
        402: (b'Payment Required', b'No payment -- see charging schemes'),
        403: (b'Forbidden', b'Request forbidden -- authorization will not help'),
        404: (b'Not Found', b'Nothing matches the given URI'),
        405: (b'Method Not Allowed', b'Specified method is invalid for this resource.'),
        406: (b'Not Acceptable', b'URI not available in preferred format.'),
        407: (b'Proxy Authentication Required', b'You must authenticate with this proxy before proceeding.'),
        408: (b'Request Timeout', b'Request timed out; try again later.'),
        409: (b'Conflict', b'Request conflict.'),
        410: (b'Gone', b'URI no longer exists and has been permanently removed.'),
        411: (b'Length Required', b'Client must specify Content-Length.'),
        412: (b'Precondition Failed', b'Precondition in headers is false.'),
        413: (b'Request Entity Too Large', b'Entity is too large.'),
        414: (b'Request-URI Too Long', b'URI is too long.'),
        415: (b'Unsupported Media Type', b'Entity body in unsupported format.'),
        416: (b'Requested Range Not Satisfiable', b'Cannot satisfy request range.'),
        417: (b'Expectation Failed', b'Expect condition could not be satisfied.'),
        500: (b'Internal Server Error', b'Server got itself in trouble'),
        501: (b'Not Implemented', b'Server does not support this operation'),
        502: (b'Bad Gateway', b'Invalid responses from another server/proxy.'),
        503: (b'Service Unavailable', b'The server cannot process the request due to a high load'),
        504: (b'Gateway Timeout', b'The gateway server did not receive a timely response'),
        505: (b'Protocol Version Not Supported', b'Cannot fulfill request.'),
    }

    def __bytes__(self) -> bytes:
        reason_phrase = self.reason_phrase or self.STATUS_CODE_MAP[self.status_code][0]

        return b'ICAP/1.0 ' + str(self.status_code).encode() + b' ' + reason_phrase + b'\r\n'
