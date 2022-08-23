import json


from shapely.geometry import Point, LineString, mapping

from .core_utils import SpatialNode, SpatialEdge, SpatialGraph


def convert_spatial_node_to_geojson(node: SpatialNode):
    """Returns a geojson representation of a SpatialNode

    Args:
        node (SpatialNode): a SpatialNode to convert.

    Returns:
        dict: a geojson representation of the SpatialNode
            {"type": "Feature", "properties": properties, "geometry": geometry}
    """
    properties = {k: v for k, v in node.attributes.items() if k != "geometry"}

    properties["object_type"] = "SpatialNode"

    geometry = mapping(node["geometry"])

    return {"type": "Feature", "properties": properties, "geometry": geometry}


def convert_spatial_edge_to_geojson(edge: SpatialEdge):
    """Returns a geojson representation of a SpatialEdge

    Args:
        node (SpatialEdge): a SpatialEdge to convert.

    Returns:
        dict: a geojson representation of the SpatialEdge
            {"type": "Feature", "properties": properties, "geometry": geometry}
    """
    properties = {k: v for k, v in edge.attributes.items() if k != "geometry"}

    properties["object_type"] = "SpatialEdge"

    geometry = mapping(
        edge["geometry"] if edge["geometry"] is not None else LineString()
    )

    return {"type": "Feature", "properties": properties, "geometry": geometry}


def convert_graph_to_geojson(
    graph: SpatialGraph, include_nodes: bool = True, include_edges: bool = True
):
    """Returns a geojson representation of a SpatialGraph

    Args:
        graph (SpatialGraph): a SpatialGraph to convert.
        include_nodes (bool, optional): whether to include nodes.
            Be aware that edges cannot be added without pre-existing nodes.
            Defaults to True.
        include_edges (bool, optional): whether to include edges.
            Defaults to True.

    Returns:
        dict: a geojson representation of the SpatialGraph
            {"type": "FeatureCollection", "features": nodes + edges}
    """
    nodes = (
        [convert_spatial_node_to_geojson(n) for n in graph._get_nodes()]
        if include_nodes
        else []
    )

    edges = (
        [convert_spatial_edge_to_geojson(e) for e in graph._get_edges()]
        if include_edges
        else []
    )

    return {"type": "FeatureCollection", "features": nodes + edges}


def convert_geojson_data_to_spatial_graph(geojson_data: dict):
    """Returns a SpatialGraph from a geojson dictionary.

    Each object in the `features` key should contain an `object_type` key
    that should be either `SpatialNode` or `SpatialEdge`.
    In the `properties`, we should find the mandatory arguments for a `SpatialNode`
    (`name`, `geometry`) or for a `SpatialEdge` (`start`, `stop`).
    See classes `SpatialNode` and `SpatialEdge` for more information.

    Args:
        geojson_data (dict): a geojson dict.
            {"type": "FeatureCollection", "features": nodes + edges}
            where nodes and edges are list of dictionaries with
            {"type": "Feature", "properties": properties, "geometry": geometry}

    Returns:
        SpatialGraph: a SpatialGraph.
    """
    nodes, edges = [], []
    for o in geojson_data["features"]:

        properties = o["properties"].copy()
        object_type = properties.pop("object_type")

        if object_type == "SpatialNode":

            name = properties.pop("name")

            nodes.append(
                SpatialNode(
                    name=name,
                    geometry=Point(o["geometry"]["coordinates"]),
                    **properties
                )
            )
        elif object_type == "SpatialEdge":
            start = properties.pop("start")
            stop = properties.pop("stop")
            geometry = o["geometry"]["coordinates"]

            if len(geometry) == 0:
                geometry = None
            else:
                geometry = LineString(geometry)

            edges.append(SpatialEdge(start=start, stop=stop, geometry=geometry))

    return SpatialGraph(nodes=nodes, edges=edges)


def read_spatial_graph_from_geojson_file(filename: str):
    """Reads a geojson file and returns a SpatialGraph.

    To understand the properties needed in the geojson file,
    see the `convert_geojson_data_to_spatial_graph` function doc.

    Args:
        filename (str): a geojson file containing SpatialGraph data.

    Returns:
        SpatialGraph: a SpatialGraph.
    """
    with open(filename, "r") as file:
        geojson_data = json.load(file)

    return convert_geojson_data_to_spatial_graph(geojson_data=geojson_data)


def write_spatial_graph_to_geojson_file(
    graph: SpatialGraph, filename: str = "my_spatial_graph.json"
):
    """Writes SpatialGraph data into a geojson file

    Args:
        graph (SpatialGraph): a SpatialGraph.
        filename (str, optional): a filename to write into.
            Defaults to "my_spatial_graph.json".
    """
    geojson_data = convert_graph_to_geojson(graph=graph)

    with open(filename, "w") as file:
        json.dump(geojson_data, file)
