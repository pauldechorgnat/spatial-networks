"""
Contains basic data structures:

- SpatialNode
- SpatialEdge
- SpatialGraph

And verification functions:

- check_node
- check_edge
"""

from collections.abc import Mapping

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPoint
from networkx import Graph
from networkx import MultiGraph


class SpatialNode(Mapping):
    def __init__(self, name: str, geometry: Point, **attr):
        self.name = name
        self.geometry = geometry
        self.attributes = {**attr, **{"name": name, "geometry": geometry}}

    def __getitem__(self, attr_name):
        return self.attributes[attr_name]

    def __contains__(self, attr_name):
        return attr_name in self.attributes

    def __len__(self):
        return len(self.attributes)

    def __iter__(self):
        return iter(self.attributes)

    def __setitem__(self, attr_name, attr_value):
        self.attributes[attr_name] = attr_value

    def __str__(self):
        return f"SpatialNode '{self.name}' with coordinates: {self.geometry}"


class SpatialEdge(Mapping):
    def __init__(self, start: str, end: str, geometry: LineString = None, **attr):
        self.start = start
        self.end = end
        self.geometry = geometry
        self.attributes = {**attr, **{"start": start, "end": end, "geometry": geometry}}

    def __getitem__(self, attr_name):
        return self.attributes[attr_name]

    def __contains__(self, attr_name):
        return attr_name in self.attributes

    def __len__(self):
        return len(self.attributes)

    def __iter__(self):
        return iter(self.attributes)

    def __setitem__(self, attr_name, attr_value):
        self.attributes[attr_name] = attr_value

    def __str__(self):
        return f"SpatialEdge from node '{self.start}' to node '{self.end}'"


def check_node(node: dict):
    if ("name" not in node) or ("geometry" not in node):
        raise ValueError("Nodes should be dictionaries with 'name' and 'geometry' keys")
    if not isinstance(node["geometry"], Point):
        raise TypeError(
            "'geometry' key of nodes should be an instance of class shapely.geometry.Point"
        )
    return node


def check_edge(edge: dict, nodes_dict: dict):
    if ("start" not in edge) or ("end" not in edge):
        raise ValueError("Edges should be dictionaries with 'start' and 'end' keys")
    if ("geometry" not in edge) or (not edge["geometry"]):
        try:
            start_node = nodes_dict[edge["start"]]
            end_node = nodes_dict[edge["end"]]

            edge["geometry"] = LineString(
                [start_node["geometry"], end_node["geometry"]]
            )
        except KeyError as error:
            raise KeyError(f"Node '{error}' is not in the nodes")
    else:
        if not isinstance(edge["geometry"], LineString):
            raise TypeError(
                "'geometry' key of edges should be an instance of class shapely.geometry.LineString"
            )
    if "length" not in edge:
        edge["length"] = edge["geometry"].length

    return edge


class SpatialGraph(MultiGraph):
    """Class that represents a Spatial Graphs"""

    def __init__(self, nodes: list = [], edges: list = []):
        """SpatialGraph constructor

        Args:
            nodes (list, optional): list of nodes of the Spatial MultiGraph.
            Nodes should be of the SpatialNode class or dictionaries with
            "name" (str) and "geometry"(shapely.geometry.Point) keys
            Defaults to [].
            edges (list, optional): list of edges of the Spatial MultiGraph.
            Edges should be of the SpatialEdge class or dictionaries with
            "start" (str), "end" (str) and "geometry" (shapely.geometry.LineString)
            Defaults to [].

        Raises:
            ValueError: A ValueError can be raised if geometry attribute
                of nodes are not of the same dimension
            ValueError: A ValueError can be raised if "geometry" or "name"
                are not attributes of a Node
            ValueError: A ValueError can be raised if "start", "end" or "geometry"
                are not attributes of an Edge
            TypeError: A TypeError can be raised if the "geometry" attribute of a Node
                is not of the shapely.geometry.Point class
            TypeError: A TypeError can be raised if the "geometry" attribute of an Edge
                is not of the shapely.geometry.LineString class

        """
        MultiGraph.__init__(self=self)

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

        for e in edges:
            self.add_edge(e)

    def node_properties_dict(self):
        return {n[0]: n[1] for n in self.nodes(data=True)}

    def edge_properties_dict(self):
        edge_dict_factory = {}
        for e in self.edges(data=True, keys=True):
            edge_dict_factory.get((e[0], e[1]), []).append(e[3])
        return edge_dict_factory

    def add_node(self, node_to_add):
        node = check_node(node=node_to_add)
        MultiGraph.add_node(self, node_for_adding=node["name"], **node)

    def add_edge(self, edge_to_add):
        edge = check_edge(edge=edge_to_add, nodes_dict=self.node_properties_dict())
        MultiGraph.add_edge(self, edge["start"], edge["end"], key=None, **edge)

    def draw_nodes(
        self, node_color="#EDC339", node_size=100, include_names=False, ax=None
    ):
        if not ax:
            fig, ax = plt.subplots(1, 1)
        xs, ys = [], []

        node_properties = self.node_properties_dict()
        for n in node_properties:

            xs.append(node_properties[n]["geometry"].x)
            ys.append(node_properties[n]["geometry"].y)

        ax.scatter(xs, ys, color=node_color, s=node_size)

        if include_names:
            for n in node_properties:
                node = node_properties[n]
                ax.annotate(
                    text=node["name"],
                    xy=node["geometry"].coords[0],
                    ha="center",
                    va="center",
                )
        return ax

    def get_points(self):
        return MultiPoint([n[1]["geometry"] for n in self.nodes(data=True)])

    def get_segments(self, include: list = None, exclude: list = None):
        if include:
            edges = self.edges(nbunch=include, data=True)
        else:
            edges = self.edges(data=True, keys=True)
        if exclude:
            edges = [e for e in edges if (e[0], e[1], e[2]) not in exclude]

        result = MultiLineString([e[3]["geometry"] for e in edges])
        return result

    def draw_edges(self, edge_color="#01577D", ax=None):
        if not ax:
            fig, ax = plt.subplots(1, 1)
        for e in self.edges(data=True, keys=True):
            coordinates = np.asarray(e[3]["geometry"].coords)
            ax.plot(coordinates[:, 0], coordinates[:, 1], color=edge_color, zorder=-1)
        return ax

    def draw(self, include_names=False, ax=None, include_axis=False):

        if not ax:
            fig, ax = plt.subplots(1, 1)
        self.draw_edges(ax=ax)
        self.draw_nodes(ax=ax, include_names=include_names)
        if not include_axis:
            ax.axis("off")
        return ax

    def add_edges_from(self, edges_to_add):
        for e in edges_to_add:
            self.add_edge(e)

    def add_nodes_from(self, nodes_to_add):
        for n in nodes_to_add:
            self.add_node(n)

    def remove_edge(self, edge_to_remove, key=None):
        e = (edge_to_remove["start"], edge_to_remove["end"])
        MultiGraph.remove_edge(self, e[0], e[1], key=key)

    def remove_node(self, node_to_remove):
        n = node_to_remove["name"]
        MultiGraph.remove_node(self, n)

    def remove_edges_from(self, edges_to_remove):
        for e in edges_to_remove:
            self.remove_edge(edge_to_remove=e)

    def remove_nodes_from(self, nodes_to_remove):
        for n in nodes_to_remove:
            self.remove_node(node_to_remove=n)

    def route_distance(self, node_i_name: str, node_j_name: str):
        try:
            return nx.shortest_path_length(
                self, source=node_i_name, target=node_j_name, weight="length"
            )
        except nx.NetworkXNoPath:
            return np.NaN

    def metric_distance(self, node_i_name: str, node_j_name: str):
        node_properties = self.node_properties_dict()
        node_i = node_properties[node_i_name]
        node_j = node_properties[node_j_name]

        return node_i["geometry"].distance(node_j["geometry"])

    def detour_index(self, node_i_name: str, node_j_name: str):
        return self.route_distance(node_i_name, node_j_name) / self.metric_distance(
            node_i_name, node_j_name
        )
