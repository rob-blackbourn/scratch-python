import json
from pathlib import Path
from typing import Any, List

import pkg_resources


def descend(root: Path, folder: Path):
    for item in folder.iterdir():
        if item.is_file():
            if item.suffix == '.json':
                filename = str(item)
                with open(filename, "rt") as fp:
                    recipe = json.load(fp)
                ascii_filename = item.parts[-1].lower().encode(
                    'ascii', 'ignore'
                ).decode(
                    'ascii'
                ).replace(
                    '_', ''
                ).replace(
                    ' ', '-'
                ).replace(
                    '--', '-'
                ).replace(
                    ',', '-and'
                ).replace(
                    '--', '-'
                )
                elements = []
                cuisine = recipe.get('recipeCuisine')
                if cuisine:
                    elements.append(cuisine.lo)
                keywords = recipe.get('keywords')
                if keywords:
                    elements += [
                        keyword.lower().replace(' ', '-')
                        for keyword in keywords
                    ]
                new_folder = root.joinpath(*elements)
                if not new_folder.exists():
                    new_folder.mkdir(parents=True)
                new_item = new_folder.joinpath(ascii_filename)
                item.rename(new_item)
                print(new_path)
        elif item.is_dir():
            descend(root, item)
        else:
            raise RuntimeError("Unknown type")


if __name__ == "__main__":
    root = Path("Recipes")
    descend(root, root)
