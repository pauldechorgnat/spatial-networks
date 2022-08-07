"""
Contains basic data structures:

- SpatialNode
- SpatialEdge

And verification functions:

- check_node
- check_edge
"""

from collections.abc import Mapping

from shapely.geometry import Point
from shapely.geometry import LineString


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
