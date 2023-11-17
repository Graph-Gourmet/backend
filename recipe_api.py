from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import networkx as nx
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

with open("food_data.json", "r") as json_file:
    recipe_data = json.load(json_file)


@app.route("/api/v1/recipes/similar", methods=["POST"])
def most_similar_recipes():
    try:
        nodo_inicial = int(request.args.get("id", default=4407))
        data = request.get_json()
        unwanted_ingredients = data.get("ingredients", [])

        # Filter recipes that contain unwanted ingredients
        filtered_recipes = [
            recipe
            for recipe in recipe_data
            if all(
                ingredient["ingredient"] not in unwanted_ingredients
                for ingredient in recipe["ingredients"]
            )
        ]

        # Load graph
        with open("food_graph.pkl", "rb") as file:
            G = pickle.load(file)
        connected_nodes = list(G.neighbors(nodo_inicial))
        shortest_paths = {}
        for target_recipe in connected_nodes:
            if target_recipe != nodo_inicial:
                path = nx.shortest_path(
                    G, source=nodo_inicial, target=target_recipe, weight="weight"
                )

                valid_path = [node for node in path if node in G]

                if not valid_path:
                    continue

                similarity = G[valid_path[0]][target_recipe]["weight"]
                shortest_paths[target_recipe] = (similarity, valid_path)

        # Filter recipes with unwanted ingredients
        filtered_shortest_paths = {}
        for recipe_id, (similarity, path) in shortest_paths.items():
            if all(
                ingredient["ingredient"] not in unwanted_ingredients
                for ingredient in recipe_data[recipe_id]["ingredients"]
            ):
                filtered_shortest_paths[recipe_id] = (similarity, path)

        # Sort recipes by similarity and choose top 10
        top_10_recipes = sorted(filtered_shortest_paths.items(), key=lambda x: x[1][0])[
            :10
        ]
        top_10_recipe_ids = [recipe_id for recipe_id, _ in top_10_recipes]

        # return
        top_10_filtered_recipes = [
            recipe for recipe in filtered_recipes if recipe["id"] in top_10_recipe_ids
        ]

        print(len(top_10_filtered_recipes))

        return jsonify(top_10_filtered_recipes), 200

        # # Sort recipes by similarity
        # top_10_recipes = sorted(shortest_paths.items(), key=lambda x: x[1][0])[:10]
        # top_10_recipe_ids = [recipe_id for recipe_id, _ in top_10_recipes]

        # top_10_filtered_recipes = [
        #     recipe for recipe in filtered_recipes if recipe["id"] in top_10_recipe_ids
        # ]

        # return jsonify(top_10_filtered_recipes), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
