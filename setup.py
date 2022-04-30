from setuptools import setup, find_packages

setup(
    name='icap_server',
    version='0.11',
    packages=find_packages(),
    install_requires=[
        'ecs_tools_py @ git+https://github.com/vphpersson/ecs_tools_py.git#egg=ecs_tools_py',
        'typed_argument_parser @ git+https://github.com/vphpersson/typed_argument_parser.git#egg=typed_argument_parser',
        'parsing_error @ git+https://github.com/vphpersson/parsing_error.git#egg=parsing_error'
    ]
)
