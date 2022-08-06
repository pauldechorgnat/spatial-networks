from collections.abc import Mapping

import numpy as np
from networkx import Graph

from itertools import combinations
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon


def generate_random_graph_data(n_nodes=200, edge_probability=0.3, dimension=2):
    nodes = [
        {"name": i, "geometry": Point(np.random.uniform(size=dimension))}
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
        if not isinstance(edge["geometry"], LineString):
            raise TypeError(
                "'geometry' key of edges should be an instance of class shapely.LineString"
            )
    if "length" not in edge:
        edge["length"] = edge["geometry"].length

    return edge


def get_closed_triangles(graph: Graph, nodes: list = []):
    if len(nodes) == 0:
        nodes = graph.nodes
    triangles = {}

    for n in nodes:
        neighbors = graph.neighbors()
        for n1, n2 in combinations(neighbors, 2):
            if graph.has_edge(n1, n2):
                triangles[n] = triangles.get(n, []) + [(n, n1, n2)]

    return triangles


def get_open_triangles(graph: Graph, nodes: list = []):
    if len(nodes) == 0:
        nodes = graph.nodes
    triangles = {}

    for n in nodes:
        neighbors = graph.neighbors()
        for n1, n2 in combinations(neighbors, 2):
            if not graph.has_edge(n1, n2):
                triangles[n] = triangles.get(n, []) + [(n, n1, n2)]

    return triangles


# def transform_triangles_to_faces(graph: Graph, triangles: list = []):
#     faces = []
#     for t in triangles:
#         faces.append(Polygon([graph.node_properties[n]["geometry"] for n in t]))

#     return faces


def create_circle(center: Point = Point(0, 0), radius: float = 5, nb_points: int = 10):
    center_x, center_y = np.asarray(center.coords)[0]
    points = [
        Point(
            [
                center_x + radius * np.cos(2 * np.pi * k / nb_points),
                center_y + radius * np.sin(2 * np.pi * k / nb_points),
            ]
        )
        for k in range(nb_points)
    ]

    circle = LineString(points + [points[0]])
    return circle


def create_circle_arc(
    start: Point = Point(0, 5),
    end: Point = Point(5, 0),
    center: Point = Point(0, 0),
    nb_points: int = 2,
):
    center_x, center_y = np.asarray(center.coords)[0]
    start_x, start_y = np.asarray(start.coords)[0]
    end_x, end_y = np.asarray(end.coords)[0]

    arg_start = np.arctan2(start_y - center_y, start_x - center_x)
    arg_end = np.arctan2(end_y - center_y, end_x - center_x)

    arg_arc = arg_end - arg_start
    if arg_arc < 0:
        arg_arc = 2 * np.pi + arg_arc

    radius = np.mean([start.distance(center), end.distance(center)])

    points = (
        [start]
        + [
            Point(
                center_x + radius * np.cos(arg_start + (arg_arc * i / (nb_points + 1))),
                center_y + radius * np.sin(arg_start + (arg_arc * i / (nb_points + 1))),
            )
            for i in range(1, nb_points + 1)
        ]
        + [end]
    )

    return LineString(points)


def generate_star_spatial_network_data(
    number_of_branches: int = 6, nodes_per_branch: int = 6
):
    points = {
        "node_0_0": Point([0, 0]),
        **{
            f"node_{r}_{k}": Point(
                (
                    r * np.cos(2 * np.pi * k / number_of_branches + np.pi / 2),
                    r * np.sin(2 * np.pi * k / number_of_branches + np.pi / 2),
                )
            )
            for r in range(1, nodes_per_branch)
            for k in range(number_of_branches)
        },
    }
    nodes = [SpatialNode(name=p, geometry=points[p]) for p in points]
    edges = []
    # first ring
    for k in range(number_of_branches):
        edges.append(
            SpatialEdge(
                start="node_0_0",
                end=f"node_1_{k}",
                geometry=LineString([points["node_0_0"], points[f"node_1_{k}"]]),
            )
        )
    # branches
    # for i in range(1, 1 + number_of_branches * nodes_per_branch - number_of_branches):
    for r in range(1, nodes_per_branch - 1):
        for k in range(number_of_branches):
            node_start = f"node_{r}_{k}"
            node_end = f"node_{r + 1}_{k}"
            edges.append(
                SpatialEdge(
                    start=node_start,
                    end=node_end,
                    geometry=LineString([points[node_start], points[node_end]]),
                )
            )
    return points, nodes, edges


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


class SpatialEdge(Mapping):
    def __init__(self, start: str, end: str, geometry: LineString, **attr):
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
