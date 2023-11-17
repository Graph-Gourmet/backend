import json

with open("food_data.json", "r") as json_file:
    data = json.load(json_file)

unique_ingredients = set()

for recipe in data:
    ingredients = recipe.get("ingredients", [])
    for ingredient_obj in ingredients:
        ingredient = ingredient_obj.get("ingredient", "").strip().lower()
        if ingredient and len(ingredient) <= 15:
            unique_ingredients.add(ingredient)

output = []

for ingredient in unique_ingredients:
    output.append(f'"{ingredient}"')

result = ",\n".join(output)

print(f"ingredients = [\n{result}\n];")
