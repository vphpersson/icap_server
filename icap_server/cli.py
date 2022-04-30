from typed_argument_parser import TypedArgumentParser
from argparse import ArgumentDefaultsHelpFormatter


class ICAPServerArgumentParser(TypedArgumentParser):

    class Namespace:
        service_name: str
        host: str
        port: int

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **(
                dict(
                    description=(
                        'Run an ICAP server with a REQMOD service that echos handled request lines, '
                        'performing no content adaptation.'
                    ),
                    formatter_class=ArgumentDefaultsHelpFormatter
                ) | kwargs
            )
        )

        self.add_argument(
            'service_name',
            help='The name of the service that should handle incoming ICAP requests.'
        )

        self.add_argument(
            '--host',
            help='The host address on which to listen.',
            default='127.0.0.1'
        )

        self.add_argument(
            '--port',
            help='The port on which to listen.',
            default=1344
        )
