from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import networkx as nx
import json
import copy

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

with open("food_data.json", "r") as json_file:
    recipe_data = json.load(json_file)


with open("food_graph.pkl", "rb") as file:
    G = pickle.load(file)

original_graph = copy.deepcopy(G)


def dijkstra(graph, start_node, k=1):
    distances = {node: float("infinity") for node in graph.nodes}
    distances[start_node] = 0
    visited = set()

    while len(visited) < k:
        current_node = min(
            (node for node in set(distances.keys()) - visited), key=distances.get
        )
        visited.add(current_node)

        for neighbor, weight in graph[current_node].items():
            distance = distances[current_node] + weight["weight"]
            if distance < distances[neighbor]:
                distances[neighbor] = distance

    top_k_nodes = sorted(distances, key=distances.get)[: k + 1]
    top_k_nodes.remove(start_node)

    return top_k_nodes


def meets_filter_criteria(recipe, unwanted_ingredients, filters):
    has_ingredient = any(
        ingredient["ingredient"] in unwanted_ingredients
        for ingredient in recipe["ingredients"]
    )

    return (
        not has_ingredient
        and filters["min_price"] <= recipe["price"] <= filters["max_price"]
        and filters["min_calories"]
        <= recipe["nutrition"]["calories"]
        <= filters["max_calories"]
        and filters["min_carbohydrates"]
        <= recipe["nutrition"]["carbohydrates"]
        <= filters["max_carbohydrates"]
        and filters["min_protein"]
        <= recipe["nutrition"]["protein"]
        <= filters["max_protein"]
        and filters["min_fat"] <= recipe["nutrition"]["fat"] <= filters["max_fat"]
        and filters["min_sugar"] <= recipe["nutrition"]["sugar"] <= filters["max_sugar"]
    )


# @app.route("/api/v1/recipes/similar", methods=["POST"])


@app.route("/api/v1/recipes/similar", methods=["POST"])
def top_10_recipes_endpoint_filters():
    global G
    nodo_inicial = int(request.args.get("id", default=4400))
    data = request.get_json()
    unwanted_ingredients = data.get("ingredients", [])
    filters = {
        "max_price": data.get("max_price", 1000000),
        "min_price": data.get("min_price", 0),
        "max_calories": data.get("max_calories", 1000000),
        "min_calories": data.get("min_calories", 0),
        "max_carbohydrates": data.get("max_carbohydrates", 1000000),
        "min_carbohydrates": data.get("min_carbohydrates", 0),
        "max_protein": data.get("max_protein", 1000000),
        "min_protein": data.get("min_protein", 0),
        "max_fat": data.get("max_fat", 1000000),
        "min_fat": data.get("min_fat", 0),
        "max_sugar": data.get("max_sugar", 1000000),
        "min_sugar": data.get("min_sugar", 0),
    }

    closest_recipes = []

    try:
        while len(closest_recipes) < 10:
            if len(G) < 10:
                G = copy.deepcopy(original_graph)

            if len(G) < 10:
                break

            recipe_id = dijkstra(G, nodo_inicial)
            recipe = next((i for i in recipe_data if i["id"] == recipe_id[0]), None)

            if meets_filter_criteria(recipe, unwanted_ingredients, filters):
                closest_recipes.append(recipe)

            G.remove_node(recipe_id[0])

        G = copy.deepcopy(original_graph)

        return jsonify(closest_recipes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
