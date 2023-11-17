import networkx as nx
import pickle

with open("food_graph.pkl", "rb") as file:
    G = pickle.load(file)

nodo_inicial = 4407
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


print("10 Most Similar Recipes:")
for target_recipe, (similarity, path) in sorted(
    shortest_paths.items(), key=lambda x: x[1][0]
)[:10]:
    print(f"Recipe ID: {target_recipe}, Similarity: {similarity:.2f}, Path: {path}")
