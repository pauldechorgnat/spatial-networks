import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon

from networkx import Graph
from networkx import DiGraph
from networkx.drawing import draw_networkx_nodes
from networkx.drawing import draw_networkx_edges

import warnings

warnings.filterwarnings("error")


class SpatialGraph(Graph):
    def __init__(self, nodes, edges):
        Graph.__init__(self=self)
        # nodes should be a dictionaries with a `name`` and a `geometry` keys
        # adding nodes
        dimensions = []
        for n in nodes:
            if ("name" not in n) or ("geometry" not in n):
                raise ValueError(
                    "Nodes should be dictionaries with 'name' and 'geometry' keys"
                )
            if not isinstance(n["geometry"], Point):
                raise TypeError(
                    "'geometry' key of nodes should be an instance of class shapely.Point"
                )
            dimensions.append(n["geometry"].has_z)

            self.add_node(n["name"], **n)

        if sum(dimensions) == 1:
            self.dimension = 3
        elif sum(dimensions) == 0:
            self.dimension = 2
        else:
            raise ValueError("Nodes are not all of the same dimension")

        self.node_properties = {n["name"]: n for n in nodes}
        self.edge_properties = {}

        for e in edges:
            if ("start" not in e) or ("end" not in e):
                raise ValueError(
                    "Edges should be dictionaries with 'start' and 'end' keys"
                )
            if "geometry" not in e:
                try:
                    start_node = self.node_properties[e["start"]]
                    end_node = self.node_properties[e["end"]]

                    e["geometry"] = LineString(
                        [start_node["geometry"], end_node["geometry"]]
                    )
                except KeyError as e:
                    raise KeyError(f"Node '{e}' is not in the nodes")
            else:
                if not isinstance(e["geometry"], LineString):
                    raise TypeError(
                        "'geometry' key of edges should be an instance of class shapely.LineString"
                    )
            if "length" not in e:
                e["length"] = e["geometry"].length

            self.add_edge(e["start"], e["end"], **e)
            self.edge_properties[(e["start"], e["end"])] = e

    def draw_nodes(self):
        xs, ys = [], []
        for n in self.node_properties:
            xs.append(self.node_properties[n]["geometry"].x)
            ys.append(self.node_properties[n]["geometry"].y)

        plt.scatter(xs, ys, color="b")

    def draw_edges(self):
        for e in self.edge_properties:
            coordinates = np.asarray(self.edge_properties[e]["geometry"].coords)
            plt.plot(coordinates[:, 0], coordinates[:, 1], color="r")

    def draw(self):

        self.draw_edges()
        self.draw_nodes()


if __name__ == "__main__":
    from utils import generate_random_graph_data

    nodes, edges = generate_random_graph_data(n_nodes=60, edge_probability=0.01)
    print(len(nodes))
    print(len(edges))
    spatial_graph = SpatialGraph(nodes=nodes, edges=edges)
    spatial_graph.draw()
    plt.show()
