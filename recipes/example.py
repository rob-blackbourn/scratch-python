import json
from pathlib import Path
from typing import Any, List

import docx2json

# text = docx2json.convert("Beef and oyster pie - Hairy Bikers.docx")

template = {
    "@context": "http://schema.org/",
    "@type": "Recipe",
    "name": "",
            "author": {
                "@type": "Person",
                "name": "Rob Blackbourn"
            },
    "description": "",
    "datePublished": "2019-02-15T19:59:57+00:00",
    "image": [
                "https://www.example.com/image.png",
            ],
    "recipeYield": "",
    "prepTime": "",
    "cookTime": "",
    "recipeIngredient": None,
    "recipeInstructions": None,
    "recipeCategory": [],
    "recipeCuisine": [],
    "keywords": "",
    "unparsed": []
}

def transform(lines: List[str]) -> Any:
    if not lines:
        return None

    recipe = template.copy()
    recipe['recipeIngredient'] = []
    recipe['recipeInstructions'] = []
    
    recipe['name'] = lines[0]
    in_ingredients = False
    in_method = False
    for line in lines[1:]:
        if line.lower().startswith('yield'):
            _name, _sep, value = line.partition(':')
            if value:
                recipe['recipeYield'] = value.strip()
            else:
                recipe['recipeYield'] = line
        elif line.lower().startswith('preparation time') or line.lower().startswith('prep time'):
            _name, _sep, value = line.partition(':')
            if value:
                recipe['prepTime'] = value.strip()
            else:
                recipe['prepTime'] = line
        elif line.lower().startswith('cooking time') or line.lower().startswith('cook time'):
            _name, _sep, value = line.partition(':')
            if value:
                recipe['cookTime'] = value.strip()
            else:
                recipe['cookTime'] = line
        elif line.lower().startswith('ingredients'):
            in_ingredients = True
            in_method = False
        elif line.lower() in ('method', 'preperation', 'preparation'):
            in_ingredients = False
            in_method = True
        elif in_ingredients:
            recipe['recipeIngredient'].append(line)
        elif in_method:
            recipe['recipeInstructions'].append(line)
        else:
            recipe['unparsed'].append(line)
    return recipe

def descend(folder: Path):
    for item in folder.iterdir():
        if item.is_file():
            print(f'file: {item}')
            if item.suffix == '.docx':
                text = docx2json.convert(str(item), sepBold=False)
                dct = json.loads(text)
                recipe = transform(dct['text'])
                print(recipe)
                with open(item.with_suffix('.json'), "wt") as fp:
                    json.dump(recipe, fp)
            item.unlink()
        elif item.is_dir():
            descend(item)
        else:
            raise RuntimeError("Unknown type")


if __name__ == "__main__":
    descend(Path("/home/rtb/dev/scratch/data/recipes/drive"))
