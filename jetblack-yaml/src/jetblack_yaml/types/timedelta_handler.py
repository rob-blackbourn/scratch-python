from datetime import timedelta
import re


class TimeDelta:
    yaml_tag = '!timedelta'
    yaml_pattern = re.compile(
        r'^((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?$', re.X)


    @classmethod
    def to_yaml(cls, representer, node):
        def _format_timedelta(td):
            seconds = td.seconds
            minutes = seconds // 60
            hours = minutes // 60
            weeks = td.days // 7
            days = td.days % 7
            hours %= 24
            minutes %= 60
            seconds %= 60
            s = ''
            if weeks:
                s += str(weeks) + 'w'
            if days:
                s += str(days) + 'd'
            if hours:
                s += str(hours) + 'h'
            if minutes:
                s += str(minutes) + 'm'
            if seconds or len(s) == 0:
                s += str(seconds) + 's'
            return s


        return representer.represent_scalar(cls.yaml_tag, _format_timedelta(node))


    # noinspection PyUnusedLocal
    @classmethod
    def from_yaml(cls, constructor, node):
        def _parse_timedelta(value):
            parts = cls.yaml_pattern.match(value)
            if not parts:
                return
            parts = parts.groupdict()
            time_params = {}
            for (name, param) in parts.items():
                if param:
                    time_params[name] = int(param)
            return timedelta(**time_params)


        return _parse_timedelta(node.value)


    @classmethod
    def register(cls, yaml):
        yaml.register_class(TimeDelta)
        yaml.representer.add_representer(TimeDelta, cls.to_yaml)

        # add representer for python's native datetime.timedelta class
        yaml.representer.add_representer(timedelta, cls.to_yaml)
