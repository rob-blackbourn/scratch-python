from datetime import time
import re
from yaml.dumper import Dumper
from yaml.loader import Loader
from yaml.nodes import Node, ScalarNode
from .common import add_custom_type

TIME_TAG = '!time'
TIME_REGEX = re.compile(
    r'^(?P<hour>[0-9][0-9]?):(?P<minute>[0-9][0-9]):(?P<second>[0-9][0-9])(?:\.(?P<fraction>[0-9]*))$', re.X)


def time_representer(dumper: Dumper, data: time) -> ScalarNode:
    return dumper.represent_scalar(TIME_TAG, data.isoformat())


def time_constructor(loader: Loader, node: Node) -> time:
    value = loader.construct_scalar(node)
    data = time.fromisoformat(value)
    return data


def add_custom_type_time():
    add_custom_type(time, TIME_TAG, time_representer, time_constructor, TIME_REGEX)
