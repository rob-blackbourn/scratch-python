from datetime import time
import re


class Time:
    yaml_tag = '!time'
    yaml_pattern = re.compile(
        r'^(?P<hour>[0-9][0-9]?):(?P<minute>[0-9][0-9]):(?P<second>[0-9][0-9])(?:\.(?P<fraction>[0-9]*))$', re.X)


    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.isoformat())


    # noinspection PyUnusedLocal
    @classmethod
    def from_yaml(cls, constructor, node):
        data = time.fromisoformat(node.value)
        return data


    @classmethod
    def register(cls, yaml):
        yaml.register_class(cls)
        yaml.representer.add_representer(cls, cls.to_yaml)

        yaml.representer.add_representer(time, cls.to_yaml)
