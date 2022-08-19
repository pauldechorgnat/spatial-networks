import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import MultiPoint
from shapely.geometry import MultiLineString

from networkx import Graph
from networkx import DiGraph
from networkx.drawing import draw_networkx_nodes
from networkx.drawing import draw_networkx_edges

from .utils import (
    create_circle_arc,
    generate_grid_tree_data,
    generate_soft_rgg_data,
    generate_star_spatial_network_data,
    generate_square_lattice_data,
    generate_triangle_lattice_data,
    generate_hexagonal_lattice_data,
    generate_regular_tree_data,
    generate_circular_tree_data,
    SpatialEdge,
    SpatialNode,
    SpatialGraph,
)


class SoftRGG(SpatialGraph):
    """A simple class that creates a Soft Random Geometric Graph"""

    def __init__(
        self,
        number_of_nodes: int = 30,
        position_distribution: callable = np.random.uniform,
        deterrence_function: callable = lambda x: x > 0.3,
        prefix: str = "soft_rgg",
    ):
        nodes, edges = generate_soft_rgg_data(
            n_nodes=number_of_nodes,
            position_distribution=position_distribution,
            deterrence_function=deterrence_function,
            prefix=prefix,
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class RandomSpatialGraph(SoftRGG):
    """A simple class that creates a Random Graph with random positions"""

    def __init__(
        self,
        number_of_nodes: int = 200,
        edge_probability: float = 0.01,
        position_distribution: callable = np.random.uniform,
        prefix: str = "random",
    ):
        self.deterrence_function = lambda x: np.random.uniform() < edge_probability
        self.edge_probability = edge_probability

        SoftRGG.__init__(
            self,
            number_of_nodes=number_of_nodes,
            position_distribution=position_distribution,
            prefix=prefix,
            deterrence_function=self.deterrence_function,
        )


class RandomGeometricGraph(SoftRGG):
    """A simple class that creates a Random Geometric Graph"""

    def __init__(
        self,
        number_of_nodes: int = 200,
        radius: float = 0.1,
        position_distribution: callable = np.random.uniform,
        prefix: str = "rgg",
    ):

        SoftRGG.__init__(
            self,
            number_of_nodes=number_of_nodes,
            position_distribution=position_distribution,
            deterrence_function=lambda x: x < (2 * radius),
            prefix=prefix,
        )


class StarSpatialGraph(SpatialGraph):
    """A simple class that creates a Start Geometric Graph"""

    def __init__(
        self,
        number_of_branches: int = 6,
        nodes_per_branch: int = 10,
        prefix: str = "node",
    ):

        _, nodes, edges = generate_star_spatial_network_data(
            number_of_branches=number_of_branches,
            nodes_per_branch=nodes_per_branch,
            prefix=prefix,
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class StarAndRingNetwork(SpatialGraph):
    def __init__(
        self,
        number_of_branches: int = 6,
        nodes_per_branch: int = 10,
        ring_depths: list = [5],
        prefix: str = "node",
    ):
        # building the star network
        points, nodes, edges = generate_star_spatial_network_data(
            number_of_branches=number_of_branches,
            nodes_per_branch=nodes_per_branch,
            prefix=prefix,
            ring_depths=ring_depths,
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class SquareLattice(SpatialGraph):
    """A regular square lattice"""

    def __init__(
        self,
        nb_lines: int = 5,
        squares_per_line: int = 5,
        square_height: float = 1.0,
        square_width: float = 1.0,
        prefix: str = "node",
    ):
        nodes, edges = generate_square_lattice_data(
            nb_lines=nb_lines,
            squares_per_line=squares_per_line,
            square_height=square_height,
            square_width=square_width,
            prefix=prefix,
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class TriangleLattice(SpatialGraph):
    """A regular triangle lattice"""

    def __init__(
        self,
        triangles_per_line: int = 5,
        nb_lines: int = 5,
        triangle_base: float = 1.0,
        triangle_height: float = 1.0,
        prefix: str = "node",
    ):
        nodes, edges = generate_triangle_lattice_data(
            nb_lines=nb_lines,
            triangles_per_line=triangles_per_line,
            triangle_base=triangle_base,
            triangle_height=triangle_height,
            prefix=prefix,
        )
        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class HexagonalLattice(SpatialGraph):
    """A regular hexagonal lattice"""

    def __init__(
        self,
        hexagons_per_line: int = 3,
        nb_lines: int = 4,
        hexagon_base: int = 1.0,
        prefix: str = "node",
    ):
        nodes, edges = generate_hexagonal_lattice_data(
            hexagons_per_line=hexagons_per_line,
            nb_lines=nb_lines,
            hexagon_base=hexagon_base,
            prefix=prefix,
        )
        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class RegularTree(SpatialGraph):
    def __init__(
        self,
        branching_factor: int = 3,
        tree_depth: int = 4,
        leaf_spacing: float = 1.0,
        step_size: float = 1.0,
        root: Point = Point(0, 0),
        rotation: float = 0,
        prefix: str = "node",
    ):
        nodes, edges = generate_regular_tree_data(
            branching_factor=branching_factor,
            tree_depth=tree_depth,
            leaf_spacing=leaf_spacing,
            step_size=step_size,
            root=root,
            rotation=rotation,
            prefix=prefix,
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class GridTree(SpatialGraph):
    def __init__(
        self,
        suburb_depth: int = 4,
        suburb_branching_factor: int = 2,
        suburb_leaf_spacing: float = 1.0,
        suburb_step_size: float = 1.0,
        suburb_spacing: float = 1.0,
        inner_square_height: float = 1.0,
        inner_square_width: float = 1.0,
        inner_semi_width: int = 5,
        inner_semi_height: int = 5,
    ):

        nodes, edges = generate_grid_tree_data(
            suburb_depth=suburb_depth,
            suburb_branching_factor=suburb_branching_factor,
            suburb_leaf_spacing=suburb_leaf_spacing,
            suburb_step_size=suburb_step_size,
            suburb_spacing=suburb_spacing,
            inner_square_height=inner_square_height,
            inner_square_width=inner_square_width,
            inner_semi_width=inner_semi_width,
            inner_semi_height=inner_semi_height,
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class CircularTree(SpatialGraph):
    def __init__(
        self,
        branching_factor: int = 4,
        tree_depth: int = 4,
        ring_depths: list = [],
        step_size: list = 1.0,
        prefix: str = "circular_tree",
        root: Point = Point(0, 0),
    ):
        nodes, edges = generate_circular_tree_data(
            branching_factor=branching_factor,
            tree_depth=tree_depth,
            ring_depths=ring_depths,
            step_size=step_size,
            prefix=prefix,
            root=root,
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


if __name__ == "__main__":

    star_and_ring_network = StarAndRingNetwork(
        number_of_branches=8, nodes_per_branch=6, ring_depths=[2, 5]
    )
    print(str(star_and_ring_network))
    star_and_ring_network.draw(include_names=True)
    plt.show()
