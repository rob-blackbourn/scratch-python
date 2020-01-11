import json
from pathlib import Path
from typing import Any, List

import docx2json
import pkg_resources

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
    "recipeCategory": None,
    "recipeCuisine": None,
    "keywords": "",
    "tool": None,
    "unparsed": None
}

def transform(lines: List[str], cuisine: str, keywords) -> Any:
    if not lines:
        return None

    recipe = template.copy()
    recipe['recipeIngredient'] = []
    recipe['recipeInstructions'] = []
    recipe['tool'] = []
    recipe['unparsed'] = []
    
    recipe['name'] = lines[0]
    recipe['recipeCuisine'] = cuisine
    recipe['keywords'] = keywords
    section = None
    in_ingredients = False
    in_method = False
    in_tool = False
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
            section = 'ingredients'
        elif line.lower().startswith('equipment'):
            section = 'tool'
        elif line.lower() in ('method', 'preperation', 'preparation'):
            section = 'method'
        elif section == 'ingredients':
            recipe['recipeIngredient'].append(line)
        elif section == 'method':
            recipe['recipeInstructions'].append(line)
        elif section == 'tool':
            recipe['tool'].append({
                '@type': 'HowToTool',
                'name': line
            })
        else:
            section = None
            recipe['unparsed'].append(line)

    if not recipe['unparsed']:
        del recipe['unparsed']

    return recipe

def descend(folder: Path):
    for item in folder.iterdir():
        if item.is_file():
            if item.suffix == '.docx':
                filename = str(item)
                cuisine = item.parts[1]
                keywords = list(item.parts[2:-1])
                text = docx2json.convert(filename, sepBold=False)
                dct = json.loads(text)
                recipe = transform(dct['text'], cuisine, keywords)
                with open(item.with_suffix('.json'), "wt") as fp:
                    json.dump(recipe, fp, indent=2)
            item.unlink()
        elif item.is_dir():
            descend(item)
        else:
            raise RuntimeError("Unknown type")


if __name__ == "__main__":
    descend(Path("Recipes"))
