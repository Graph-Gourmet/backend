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


@app.route("/api/v1/recipes/similar", methods=["POST"])
def top_10_recipes_endpoint():
    global G
    nodo_inicial = int(request.args.get("id", default=4400))
    data = request.get_json()
    unwanted_ingredients = data.get("ingredients", [])

    closest_recipes = []

    while len(closest_recipes) < 10:
        recipe_id = dijkstra(G, nodo_inicial)
        recipe = next((i for i in recipe_data if i["id"] == recipe_id[0]), None)

        has_ingredient = any(
            ingredient["ingredient"] in unwanted_ingredients
            for ingredient in recipe["ingredients"]
        )

        if not has_ingredient:
            closest_recipes.append(recipe)

        G.remove_node(recipe_id[0])

    G = copy.deepcopy(original_graph)

    return jsonify(closest_recipes), 200


if __name__ == "__main__":
    app.run(debug=True)
