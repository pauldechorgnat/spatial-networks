from itertools import combinations

import numpy as np
import networkx as nx

from networkx import Graph
from shapely.ops import split as shapely_split
from shapely.geometry import Point
from shapely.geometry import LineString

from .core_utils import SpatialEdge
from .core_utils import SpatialNode
from .core_utils import SpatialGraph

from .geometry_utils import consistent_intersection


def merge(
    left: Graph, right: Graph, left_prefix: str = "left", right_prefix: str = "right"
):
    pass


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


def make_planar(
    graph: SpatialGraph, keep_data: bool = True, prefix: str = "intersection"
):
    """Function that returns a new SpatialGraph made planar by splitting crossing edges

    Args:
        graph (SpatialGraph): A SpatialGraph
        keep_data (bool, optional): Boolean to keep node and edges data (edges that are splitted cannot keep the data).
            Defaults to True.
        prefix (str, optional): Prefix for the newly created nodes.
            Defaults to "intersection".

    Returns:
        SpatialGraph: a planarized version of graph
    """
    if keep_data:
        points = {
            (n[1]["geometry"].x, n[1]["geometry"].y): {
                **{k: v for k, v in n[1].items() if k != "geometry"}
            }
            for n in graph.nodes(data=True)
        }
    else:
        points = {
            (n[1]["geometry"].x, n[1]["geometry"].y): {"name": f"node_{i}"}
            for i, n in enumerate(graph.nodes(data=True))
        }
    edges = []

    counter = 0

    new_graph = SpatialGraph()

    for edge in graph.edges(data=True, keys=True):
        segments = graph.get_segments(exclude=[(edge[0], edge[1], edge[2])])
        old_edge = False

        intersections = consistent_intersection(edge[3]["geometry"], segments)
        for i in intersections.geoms:
            x, y = np.asarray(i.coords)[0]
            if (x, y) not in points:
                points[(x, y)] = {"name": f"{prefix}_{counter}"}
                counter += 1
        if segments.type == "GeometryCollection":
            new_edges = [edge[3]["geometry"]]
        else:
            new_edges = shapely_split(geom=edge[3]["geometry"], splitter=segments).geoms

        for new_edge in new_edges:
            coords = np.asarray(new_edge.coords)
            [x_start, y_start], [x_end, y_end] = coords[0], coords[-1]

            edges.append(
                SpatialEdge(
                    start=points[(x_start, y_start)]["name"],
                    end=points[(x_end, y_end)]["name"],
                    geometry=new_edge,
                    old_index=edge[2],
                )
            )
    nodes = [SpatialNode(geometry=Point(k), **v) for k, v in points.items()]

    if keep_data:
        for i, e in enumerate(edges):
            if graph.has_edge(e.start, e.end):
                edges[i] = SpatialEdge(
                    **graph.get_edge_data(e.start, e.end)[e.get("old_index", 0)]
                )

    new_graph.add_nodes_from(nodes_to_add=nodes)
    new_graph.add_edges_from(edges_to_add=edges)

    return new_graph


def flatten_graph(graph: SpatialGraph):
    """Function to make all edges into straight lines

    Args:
        graph (SpatialGraph): graph to flatten

    Returns:
        SpatialGraph: a SpatialGraph with straight lines as edges
    """
    nodes = [SpatialNode(**i[1]) for i in graph.nodes(data=True)]

    edges = [SpatialEdge(start=start, end=end) for start, end in graph.edges()]

    new_graph = SpatialGraph(nodes=nodes, edges=edges)

    return new_graph
