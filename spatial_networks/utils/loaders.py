import pkg_resources
import json

from .graph_io import (
    convert_geojson_data_to_spatial_graph,
    read_spatial_graph_from_geojson_file,
)


def load_paris_subway():
    """Returns a SpatialGraph of Paris Subway stations.

    Returns:
        SpatialGraph: a SpatialGraph of Paris Subway stations
    """
    data = pkg_resources.resource_stream(
        __name__.split(".")[0], "/data/paris_subway.json"
    ).read()
    geojson_data = json.loads(data)

    return convert_geojson_data_to_spatial_graph(geojson_data=geojson_data)
