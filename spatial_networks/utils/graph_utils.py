from itertools import combinations

import networkx as nx

from networkx import Graph
from shapely.ops import split as shapely_split
from shapely.geometry import Point
from shapely.geometry import LineString

from .core_utils import SpatialEdge
from .core_utils import SpatialNode
from .core_utils import SpatialGraph


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
            (n[1]["geometry"].x, n[1]["geometry"].y): f"node_{i}"
            for i, n in enumerate(graph.nodes(data=True))
        }
    edges = []

    counter = 0

    new_graph = SpatialGraph()

    for edge in my_graph.edges(data=True):
        segments = my_graph.get_segments(exclude=[(edge[0], edge[1])])
        intersections = edge[2]["geometry"].intersection(segments)
        if isinstance(intersections, LineString):
            edges.append(
                SpatialEdge(start=edge[0], end=edge[1], geometry=edge[2]["geometry"])
            )
        else:
            for i in intersections.geoms:
                x, y = np.asarray(i.coords)[0]
                if (x, y) not in points:
                    points[(x, y)] = {"name": f"{prefix}_{counter}"}
                    counter += 1
            new_edges = shapely_split(geom=edge[2]["geometry"], splitter=segments)

            for new_edge in new_edges.geoms:
                coords = np.asarray(new_edge.coords)
                [x_start, y_start], [x_end, y_end] = coords[0], coords[-1]
                edges.append(
                    SpatialEdge(
                        start=points[(x_start, y_start)]["name"],
                        end=points[(x_end, y_end)]["name"],
                        geometry=new_edge,
                    )
                )

    nodes = [SpatialNode(geometry=Point(k), **v) for k, v in points.items()]

    if keep_data:
        for i, e in enumerate(edges):
            if graph.has_edge(e.start, e.end):
                edges[i] = SpatialEdge(**graph.get_edge_data(e.start, e.end))

    new_graph.add_nodes_from(nodes_to_add=nodes)
    new_graph.add_edges_from(edges_to_add=edges)

    return new_graph
