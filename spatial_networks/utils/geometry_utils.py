import numpy as np

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiPoint
from shapely.geometry import GeometryCollection
from shapely.affinity import rotate

from .core_utils import SpatialGraph
from .core_utils import SpatialNode
from .core_utils import SpatialEdge


def create_circle(center: Point = Point(0, 0), radius: float = 5, nb_points: int = 10):
    """Returns a LineString representing a circle.

    Args:
        center (Point, optional): center of the circle.
            Defaults to Point(0, 0).
        radius (float, optional): radius of the circle.
            Defaults to 5.
        nb_points (int, optional): number of points in the LineString.
            Increasing this will increase the 'roundness' of the circle.
            Defaults to 10.

    Returns:
        LineString: a Linestring representing a circle.
    """
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
    stop: Point = Point(5, 0),
    center: Point = Point(0, 0),
    nb_points: int = 2,
):
    """Returns a LineString representing a circle arc.

    Args:
        start (Point, optional): start of the circle arc.
            Defaults to Point(0, 5).
        stop (Point, optional): end of the circle arc.
            Defaults to Point(5, 0).
        center (Point, optional): center of the circle arc.
            Defaults to Point(0, 0).
        nb_points (int, optional): number of points in the circle arc.
            Increasing this will increase the 'roundness' of the circle arc.
            Defaults to 2.

    Returns:
        LineString: a Linestring representing a circle arc.
    """
    center_x, center_y = np.asarray(center.coords)[0]
    start_x, start_y = np.asarray(start.coords)[0]
    stop_x, stop_y = np.asarray(stop.coords)[0]

    arg_start = np.arctan2(start_y - center_y, start_x - center_x)
    arg_stop = np.arctan2(stop_y - center_y, stop_x - center_x)

    arg_arc = arg_stop - arg_start
    if arg_arc < 0:
        arg_arc = 2 * np.pi + arg_arc

    radius = np.mean([start.distance(center), stop.distance(center)])

    points = (
        [start]
        + [
            Point(
                center_x + radius * np.cos(arg_start + (arg_arc * i / (nb_points + 1))),
                center_y + radius * np.sin(arg_start + (arg_arc * i / (nb_points + 1))),
            )
            for i in range(1, nb_points + 1)
        ]
        + [stop]
    )

    return LineString(points)


def consistent_intersection(geom, splitter):
    """Returns shapely intersections as MultiPoint.
    `.intersection` method in shapely 1.8.3 returns inconsistent classes.
    This function helps to make it more consistent.

    Args:
        geom : any shapely geometric object.
        splitter : any shapely geometric object

    Raises:
        TypeError: if the intersections are not Point, MultiPoint or GeometryCollection.

    Returns:
        shapely.geometry.MultiPoint: a set of intersection points between geom and splitter.
    """
    intersections = geom.intersection(splitter)

    if isinstance(intersections, LineString):

        return MultiPoint()
    elif isinstance(intersections, Point):
        return MultiPoint([intersections])
    elif isinstance(intersections, MultiPoint):
        return intersections
    elif isinstance(intersections, GeometryCollection):
        if len(intersections.geoms) == 0:
            return MultiPoint()

    else:
        raise TypeError(
            f"intersections returned an object of type {type(intersections)} "
            "which is not yet supported."
        )


def rotate_graph(graph: SpatialGraph, angle: float = 90, origin: Point = "center"):
    """Returns a rotated SpatialGraph

    Args:
        graph (SpatialGraph): graph to rotate.
        angle (float, optional): rotation angle in degrees.
            Defaults to 90.
        origin (Point, optional): center of the rotation.
            Defaults to "center".

    Returns:
        SpatialGraph: rotated SpatialGraph
    """
    new_points = rotate(graph.get_points(), angle=angle, origin=origin)
    new_segments = rotate(graph.get_segments(), angle=angle, origin=origin)

    nodes = [
        SpatialNode(**{**old_data[1], "geometry": new_position})
        for new_position, old_data in zip(new_points.geoms, graph.nodes(data=True))
    ]

    edges = [
        SpatialEdge(**{**old_data[3], "geometry": new_segment})
        for new_segment, old_data in zip(
            new_segments.geoms, graph.edges(data=True, keys=True)
        )
    ]

    return SpatialGraph(nodes=nodes, edges=edges)
