import yaml

def add_custom_type(typ, tag, representer, constructor, pattern):
    yaml.add_representer(typ, representer)
    yaml.add_constructor(tag, constructor)
    yaml.add_implicit_resolver(tag, pattern)