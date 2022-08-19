import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiPoint
from shapely.geometry import MultiLineString


def plot_shapely_objects(
    objects: list,
    ax=None,
    figsize: tuple = (5, 5),
    point_color: str = "b",
    point_size: int = 100,
):
    """Plots a list of shapely objects.
    Mostly used for debugging.

    Args:
        objects (list): a list of shapely objects to plot.
        ax: Matplotlib Axes object.
            Defaults to None.
        figsize (tuple, optional): size of the figure if ax is None.
            Defaults to (5, 5).
        point_color (str, optional): color used to represent points.
            Defaults to "b".
        point_size (int, optional): size used to represent points.
            Defaults to 100.

    Returns:
        Matplotlib Axes object.
    """

    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=figsize)

    for o in objects:
        if isinstance(o, Point):
            ax.scatter(o.x, o.y, color=point_color, s=point_size)
        elif isinstance(o, MultiPoint):
            for p in o.geoms:
                ax.scatter(p.x, p.y, color=point_color, s=point_size)
        elif isinstance(o, LineString):
            ax.plot(
                np.asarray(o.coords)[:, 0],
                np.asarray(o.coords)[:, 1],
                zorder=-1,
            )
        elif isinstance(o, MultiLineString):
            for l in o.geoms:
                ax.plot(
                    np.asarray(l.coords)[:, 0],
                    np.asarray(l.coords)[:, 1],
                    zorder=-1,
                )

    return ax


if __name__ == "__main__":
    point = Point(0, 0)
    multi_point = MultiPoint([Point(1, 1), Point(2, 2)])
    line = LineString([Point(3, 3), Point(4, 4)])
    multi_line = MultiLineString(
        [
            LineString([Point(-1, -1), Point(0, 0)]),
            LineString([Point(0, 0), Point(0, 1)]),
        ]
    )

    plot_shapely_objects(objects=[point, multi_point, line, multi_line])
    plt.show()
