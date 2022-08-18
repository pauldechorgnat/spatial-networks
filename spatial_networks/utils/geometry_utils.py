import numpy as np

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiPoint
from shapely.geometry import GeometryCollection


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


def consistent_intersection(geom, splitter):
    """Helper function that returns a MultiPoint object for intersections"""
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
            f"intersections returned an object of type {type(intersections)}"
        )
