import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString


def plot_shapely_objects(objects, ax=None, point_color="b", point_size=100):
    """Helper to plot multiple shapely objects at once
    Mostly used for debugging"""

    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    for o in objects:
        if isinstance(o, Point):
            ax.scatter(o.x, o.y, color=point_color, s=point_size)
        elif isinstance(o, LineString):
            ax.plot(
                np.asarray(o.coords)[:, 0],
                np.asarray(o.coords)[:, 1],
                # color="r",
                zorder=-1,
            )

    return ax
