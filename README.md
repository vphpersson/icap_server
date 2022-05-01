# icap_server

A toy ICAP server library.

Supports both `REQMOD` and `RESPMOD` requests. Does not currently support previewing or error responses.

Includes a CLI component that runs the server with a `REQMOD` service that echos the request lines that the server handles.

## CLI usage

```
usage: icap_server.py [-h] [--host HOST] [--port PORT] service_name

Run an ICAP server with a REQMOD service that echos handled request lines, performing no content adaptation.

positional arguments:
  service_name  The name of the service that should handle incoming ICAP requests.

options:
  -h, --help    show this help message and exit
  --host HOST   The host address on which to listen. (default: 127.0.0.1)
  --port PORT   The port on which to listen. (default: 1344)
```

### Example

`squid.conf`:
```
[...]
icap_enable on
icap_service service_avi_req reqmod_precache icap://127.0.0.1:7878/echo
adaptation_access service_avi_req allow all
# icap_service service_avi_resp respmod_precache icap://127.0.0.1:7878/echo
# adaptation_access service_avi_resp allow all
[...]
```

```
$ ./icap_server.py --port 7878 'echo'
GET http://example.com/ HTTP/1.1
GET http://example.com/favicon.ico HTTP/1.1
CONNECT news.ycombinator.com:443 HTTP/1.1
GET https://news.ycombinator.com/ HTTP/1.1
CONNECT incoming.telemetry.mozilla.org:443 HTTP/1.1
GET https://news.ycombinator.com/news.css?5eYyZbFhPFukXyt5EaSy HTTP/1.1
CONNECT news.ycombinator.com:443 HTTP/1.1
GET https://news.ycombinator.com/grayarrow.gif HTTP/1.1
{"error": {"message": "Connection lost", "stack_trace": "File \"/home/vph/code/py/icap_server/icap_server/__init__.py\", line 63, in handle\n  await writer.drain()\nFile \"/usr/lib/python3.10/asyncio/streams.py\", line 372, in drain\n  await self._protocol._drain_helper()\nFile \"/usr/lib/python3.10/asyncio/streams.py\", line 171, in _drain_helper\n  raise ConnectionResetError('Connection lost')", "type": "builtins.ConnectionResetError"}, "event": {"created": "2022-04-30 21:56:27.505123+02:00", "sequence": 0, "timezone": "+02:00"}, "host": {"architecture": "x86_64", "hostname": "...", "name": "...", "uptime": 21743, "os": {"kernel": "...", "type": "linux"}}, "log": {"level": "ERROR", "logger": "ecs_tools_py.make_log_handler.<locals>.ECSLoggerHandler", "origin": {"file": {"path": "/home/vph/code/py/icap_server/icap_server/__init__.py", "name": "__init__.py", "line": 65}, "function": "handle"}}, "process": {"args": ["python", "./icap_server.py", "--port", "7878", "echo"], "arg_count": 5, "command_line": "python ./icap_server.py --port 7878 echo", "executable": "/usr/bin/python3.10", "name": "python3.10", "pid": 173039, "start": "2022-04-30 21:55:27.420000+02:00", "thread": {"id": 139720885614400, "name": "MainThread"}, "title": "MainProcess", "uptime": 60, "working_directory": "/home/vph/code/py/icap_server", "parent": {"pid": 166082}, "user": {"id": "1000", "name": "vph", "effective": {"id": "1000", "name": "vph"}}, "group": {"id": "1000", "name": "vph", "effective": {"id": "1000", "name": "vph"}}}, "message": "An exception occurred when writing an ICAP response."}
```

:thumbsup:

(Note the error message on the last row! It was produced by a log handler from my [ecs_tools_py](https://github.com/vphpersson/ecs_tools_py) library, which is used in this project!)

## References

- [RFC 3507 - Internet Content Adaptation Protocol (ICAP)](https://datatracker.ietf.org/doc/html/rfc3507)