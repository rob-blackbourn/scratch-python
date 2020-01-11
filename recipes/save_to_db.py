import json
from pathlib import Path
import sqlite3
from typing import Any, List
from uuid import uuid4

import pkg_resources
PROPERTY_NAMES = [
    "author"
    "description",
    "datePublished",
    "prepTime",
    "cookTime",
    "totalTime",
    "recipeIngredient",
    "recipeInstructions",
    "recipeCategory",
    "recipeCuisine",
    "keywords",
    "tool"
]


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
create table recipe(
    identifier TEXT PRIMARY KEY,
    content TEXT NOT NULL
)
""")
    conn.commit()

    conn.execute("""
create table properties(
    property_name TEXT PRIMARY KEY
)
""")
    conn.commit()

    for property_name in PROPERTY_NAMES:
        conn.execute(
            "INSERT INTO properties(property_name) VALUES (?)",
            (property_name,)
        )
    conn.commit()

    conn.execute("""
create table property_map(
    property_name TEXT NOT NULL,
    property_value TEXT NOT NULL,
    identifier TEXT NOT NULL,

    PRIMARY KEY (property_name, property_value, identifier),
    FOREIGN KEY (property_name) REFERENCES properties(property_name),
    FOREIGN KEY (identifier) REFERENCES recipes(identifier)
)
""")
    conn.commit()


def descend(folder: Path, conn: sqlite3.Connection) -> None:
    for item in folder.iterdir():
        if item.is_file():
            if item.suffix == '.json':
                filename = str(item)
                with open(filename, "rt") as fp:
                    recipe = json.load(fp)
                identifier = str(uuid4())
                recipe['identifier'] = identifier
                recipe_text = json.dumps(recipe)
                conn.execute(
                    "INSERT INTO recipe(identifier, content) VALUES (?, ?)",
                    (identifier, recipe_text)
                )
                for property_name in PROPERTY_NAMES:
                    property_value = recipe.get(property_name)
                    if not property_value:
                        continue
                    if property_name == 'keywords':
                        for keyword in property_value:
                            conn.execute(
                                'INSERT INTO property_map(property_name, property_value, identifier) VALUES (?, ?, ?)',
                                (property_name, keyword, identifier)
                            )
                    elif isinstance(property_value, str):
                        conn.execute(
                            'INSERT INTO property_map(property_name, property_value, identifier) VALUES (?, ?, ?)',
                            (property_name, property_value, identifier)
                        )
                conn.commit()

        elif item.is_dir():
            descend(item, conn)
        else:
            raise RuntimeError("Unknown type")


if __name__ == "__main__":
    conn = sqlite3.connect('recipes.db')
    init_db(conn)
    root = Path("recipes")
    descend(root, conn)
