from typing import Optional, Pattern, TypeVar, Type, Callable
import yaml
from yaml.dumper import Dumper
from yaml.loader import Loader
from yaml.nodes import Node

T = TypeVar('T')
Representer = Callable[[Dumper, T], Node]
Constructor = Callable[[Loader, Node], Optional[T]]


def add_custom_type(
        typ: Type['T'],
        tag: str,
        representer: Representer,
        constructor: Constructor,
        pattern: Optional[Pattern]
) -> None:
    yaml.add_representer(typ, representer)
    yaml.add_constructor(tag, constructor)
    if pattern is not None:
        yaml.add_implicit_resolver(tag, pattern)
