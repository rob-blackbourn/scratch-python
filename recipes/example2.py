import json
from pathlib import Path
from typing import Any, List

import pkg_resources


def descend(folder: Path):
    for item in folder.iterdir():
        if item.is_file():
            if item.suffix == '.json':
                filename = str(item)
                with open(filename, "rt") as fp:
                    recipe = json.load(fp)
                ascii_filename = filename.lower().encode(
                    'ascii', 'ignore'
                ).decode('ascii').replace(' ', '-')
                print(ascii_filename)
        elif item.is_dir():
            descend(item)
        else:
            raise RuntimeError("Unknown type")


if __name__ == "__main__":
    descend(Path("Recipes"))
