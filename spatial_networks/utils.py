import numpy as np

from shapely.geometry import Point
from shapely.geometry import LineString


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


def check_node(node: dict):
    if ("name" not in node) or ("geometry" not in node):
        raise ValueError("Nodes should be dictionaries with 'name' and 'geometry' keys")
    if not isinstance(node["geometry"], Point):
        raise TypeError(
            "'geometry' key of nodes should be an instance of class shapely.Point"
        )
    return node


def check_edge(edge: dict, nodes_dict: dict):
    if ("start" not in edge) or ("end" not in edge):
        raise ValueError("Edges should be dictionaries with 'start' and 'end' keys")
    if "geometry" not in edge:
        try:
            start_node = nodes_dict[edge["start"]]
            end_node = nodes_dict[edge["end"]]

            edge["geometry"] = LineString(
                [start_node["geometry"], end_node["geometry"]]
            )
        except KeyError as error:
            raise KeyError(f"Node '{error}' is not in the nodes")
    else:
        if not isinstance(e["geometry"], LineString):
            raise TypeError(
                "'geometry' key of edges should be an instance of class shapely.LineString"
            )
    if "length" not in edge:
        edge["length"] = edge["geometry"].length

    return edge
