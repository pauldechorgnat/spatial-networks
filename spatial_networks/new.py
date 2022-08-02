import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon

from networkx import Graph
from networkx import DiGraph
from networkx.drawing import draw_networkx_nodes
from networkx.drawing import draw_networkx_edges

from utils import check_node
from utils import check_edge

import warnings

warnings.filterwarnings("error")


class SpatialGraph(Graph):
    def __init__(self, nodes, edges):
        Graph.__init__(self=self)
        # nodes should be a dictionaries with a `name`` and a `geometry` keys
        # adding nodes
        dimensions = []
        for n in nodes:
            self.add_node(n)
            dimensions.append(n["geometry"].has_z)

        if sum(dimensions) == 1:
            self.dimension = 3
        elif sum(dimensions) == 0:
            self.dimension = 2
        else:
            raise ValueError("Nodes are not all of the same dimension")

        self.node_properties = {n["name"]: n for n in nodes}
        self.edge_properties = {}

        for e in edges:

            self.add_edge(e)
            self.edge_properties[(e["start"], e["end"])] = e

    def add_node(self, new_node):
        node = check_node(node=new_node)
        Graph.add_node(self, node_for_adding=node["name"], **node)

    def add_edge(self, new_edge):
        edge = check_edge(edge=new_edge, nodes_dict=self.node_properties)
        Graph.add_edge(self, u_of_edge=edge["start"], v_of_edge=edge["end"], **edge)

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
