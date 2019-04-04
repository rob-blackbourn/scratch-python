def make_yaml():
    from ruamel.yaml import YAML

    from .timedelta_handler import TimeDelta
    from .time_handler import Time

    yaml = YAML()
    TimeDelta.register(yaml)
    Time.register(yaml)

    return yaml
