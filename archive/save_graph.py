import networkx as nx
import pickle
import json

with open(
    "C:/Users/ruizc/OneDrive/Documents/Lucas/Code/Personal Projects/Test-Random/graphs/complejidad - food graph/food_data.json",
    "r",
) as file:
    data = json.load(file)

G = nx.Graph()

for receta in data:
    G.add_node(receta["id"])

for i, receta1 in enumerate(data):
    for j, receta2 in enumerate(data):
        if i != j:
            ingredientes_comunes = len(
                set(
                    ingrediente["ingredient"] for ingrediente in receta1["ingredients"]
                ).intersection(
                    set(
                        ingrediente["ingredient"]
                        for ingrediente in receta2["ingredients"]
                    )
                )
            )
            ingredientes_totales = len(
                set(
                    ingrediente["ingredient"] for ingrediente in receta1["ingredients"]
                ).union(
                    set(
                        ingrediente["ingredient"]
                        for ingrediente in receta2["ingredients"]
                    )
                )
            )
            similitud = 1 - (ingredientes_comunes / ingredientes_totales)
            G.add_edge(receta1["id"], receta2["id"], weight=similitud)

# Save the graph to a file using pickle
with open("food_graph_backup.pkl", "wb") as file:
    pickle.dump(G, file)

print("Graph saved to food_graph.pkl")
