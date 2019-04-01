from datetime import time
import re
from .common import add_custom_type

TIME_TAG = '!time'
TIME_REGEX = re.compile(
    r'^(?P<hour>[0-9][0-9]?):(?P<minute>[0-9][0-9]):(?P<second>[0-9][0-9])(?:\.(?P<fraction>[0-9]*))$'
)

def time_representer(dumper, data: time):
    return dumper.represent_scalar(TIME_TAG, data.isoformat())

def time_constructor(loader, node):
    value = loader.construct_scalar(node)
    data = time.fromisoformat(value)
    return data

def add_custom_time():
    add_custom_type(time, TIME_TAG, time_representer, time_constructor, TIME_REGEX)
