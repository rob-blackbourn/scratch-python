from aiohttp import web
from aiohttp_route_middleware import UrlDispatcherEx
import argparse
from easydict import EasyDict as edict
import yaml

from .initialization import initialize
from . import __version__ as version


def load_config(filename):
    with open(filename, 'rt') as fp:
        config = yaml.load(fp)
    return edict(config)


def parse_args(argv: list):
    parser = argparse.ArgumentParser(
        description='JetBlack GraphQL Blog',
        add_help=False)

    parser.add_argument(
        '--help', help='Show usage',
        action='help')
    parser.add_argument(
        '--version', help='Show version',
        action='version', version='%(prog)s ' + version)
    parser.add_argument(
        '-f', '--config-file', help='Path to the configuration file.',
        action="store", dest='CONFIG_FILE')

    return parser.parse_args(argv)


def startup(argv):
    args = parse_args(argv[1:])
    config = load_config(args.CONFIG_FILE)
    start_server(config)


def start_server(config):
    app = web.Application(router=UrlDispatcherEx())

    app['config'] = config

    initialize(app)

    web.run_app(app)
