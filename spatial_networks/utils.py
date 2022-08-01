import numpy as np

from shapely.geometry import Point


def generate_random_graph_data(n_nodes=200, edge_probability=0.3):

    nodes = [
        {"name": i, "geometry": Point(np.random.uniform(size=2))}
        for i in range(n_nodes)
    ]

    edges = []

    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if np.random.uniform() > (1 - edge_probability):
                edges.append({"start": nodes[i]["name"], "end": nodes[j]["name"]})

    return nodes, edges
