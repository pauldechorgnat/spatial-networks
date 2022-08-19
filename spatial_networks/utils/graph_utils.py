from itertools import combinations

import numpy as np
import networkx as nx

from shapely.ops import split as shapely_split
from shapely.geometry import Point
from shapely.geometry import LineString

from .core_utils import SpatialEdge
from .core_utils import SpatialNode
from .core_utils import SpatialGraph

from .geometry_utils import consistent_intersection


def merge_graphs(
    left: SpatialGraph,
    right: SpatialGraph,
    left_prefix: str = "left",
    right_prefix: str = "right",
    links: list = [],
):
    """Returns a SpatialGraph from the merger of two SpatialGraph.

    Args:
        left (SpatialGraph): a SpatialGraph
        right (SpatialGraph): a SpatialGraph
        left_prefix (str, optional): a prefix to rename nodes from the left graph.
            Defaults to "left".
        right_prefix (str, optional): a prefix to rename nodes from the right graph.
            Defaults to "right".
        links (list, optional): a list of SpatialEdge to link both graphs.
            Defaults to [].

    Returns:
        SpatialGraph: a merged SpatialGraph
    """
    nodes = [
        SpatialNode(**{**n[1], "name": f"{left_prefix}_{n[1]['name']}"})
        for n in left.nodes(data=True)
    ] + [
        SpatialNode(**{**n[1], "name": f"{right_prefix}_{n[1]['name']}"})
        for n in right.nodes(data=True)
    ]

    edges = (
        [
            SpatialEdge(
                **{
                    **e[3],
                    "start": f"{left_prefix}_{e[3]['start']}",
                    "stop": f"{left_prefix}_{e[3]['stop']}",
                },
            )
            for e in left.edges(data=True, keys=True)
        ]
        + [
            SpatialEdge(
                **{
                    **e[3],
                    "start": f"{right_prefix}_{e[3]['start']}",
                    "stop": f"{right_prefix}_{e[3]['stop']}",
                },
            )
            for e in right.edges(data=True, keys=True)
        ]
        + links
    )

    return SpatialGraph(nodes=nodes, edges=edges)


def get_closed_triangles(graph: SpatialGraph, nodes: list = []):
    """returns a list of closed triangles in a graph

    Args:
        graph (SpatialGraph): graph
        nodes (list, optional): list of nodes to consider.
            Defaults to [].

    Returns:
        dict: dictionary whose values are lists of triangles
        referenced by node names.
    """
    if len(nodes) == 0:
        nodes = graph.nodes
    triangles = {}

    for n in nodes:
        neighbors = graph.neighbors()
        for n1, n2 in combinations(neighbors, 2):
            if graph.has_edge(n1, n2):
                triangles[n] = triangles.get(n, []) + [(n, n1, n2)]

    return triangles


def get_open_triangles(graph: SpatialGraph, nodes: list = []):
    """returns a list of closed triangles in a graph

    Args:
        graph (SpatialGraph): graph
        nodes (list, optional): list of nodes to consider.
            Defaults to [].

    Returns:
        dict: dictionary whose values are lists of triangles
        referenced by node names.
    """
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
            [x_start, y_start], [x_stop, y_stop] = coords[0], coords[-1]

            edges.append(
                SpatialEdge(
                    start=points[(x_start, y_start)]["name"],
                    stop=points[(x_stop, y_stop)]["name"],
                    geometry=new_edge,
                    old_index=edge[2],
                )
            )
    nodes = [SpatialNode(geometry=Point(k), **v) for k, v in points.items()]

    if keep_data:
        for i, e in enumerate(edges):
            if graph.has_edge(e.start, e.stop):
                edges[i] = SpatialEdge(
                    **graph.get_edge_data(e.start, e.stop)[e.get("old_index", 0)]
                )

    new_graph.add_nodes_from(nodes_to_add=nodes)
    new_graph.add_edges_from(edges_to_add=edges)

    return new_graph


def flatten_graph(graph: SpatialGraph):
    """Returns a copy of a SpatialGraph with all edges as straight lines.

    Args:
        graph (SpatialGraph): graph to flatten.

    Returns:
        SpatialGraph: a SpatialGraph with straight lines as edges.
    """
    nodes = [SpatialNode(**i[1]) for i in graph.nodes(data=True)]

    edges = [SpatialEdge(start=start, stop=stop) for start, stop in graph.edges()]

    new_graph = SpatialGraph(nodes=nodes, edges=edges)

    return new_graph
