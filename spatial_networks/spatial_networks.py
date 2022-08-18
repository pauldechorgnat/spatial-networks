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

# from utils import check_node
# from utils import check_edge
# from utils import create_circle_arc
# from utils import generate_star_spatial_network_data
# from utils import SpatialEdge, SpatialNode
from .utils import (
    create_circle_arc,
    generate_star_spatial_network_data,
    generate_square_lattice_data,
    generate_triangle_lattice_data,
    generate_hexagonal_lattice_data,
    generate_regular_tree_data,
    SpatialEdge,
    SpatialNode,
    SpatialGraph,
)

# import warnings

# warnings.filterwarnings("error")


class RandomSpatialGraph(SpatialGraph):
    """A simple class that creates a Random Graph with random positions"""

    def __init__(
        self,
        number_of_nodes: int = 200,
        edge_probability: float = 0.01,
        dimension: int = 2,
        position_distribution: callable = np.random.uniform,
        prefix: str = "node",
    ):
        if dimension not in [2, 3]:
            raise ValueError(f"dimension should be 2 or 3 not '{dimension}'")

        nodes = [
            SpatialNode(
                name=f"{prefix}_{i}",
                geometry=Point(position_distribution(size=dimension)),
            )
            for i in range(number_of_nodes)
        ]

        edges = []

        for i in range(number_of_nodes):
            for j in range(i + 1, number_of_nodes):
                if np.random.uniform() < edge_probability:
                    edges.append(
                        SpatialEdge(
                            start=f"{prefix}_{i}",
                            stop=f"{prefix}_{j}",
                            geometry=LineString(
                                [nodes[i]["geometry"], nodes[j]["geometry"]]
                            ),
                        )
                    )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class SoftRGG(SpatialGraph):
    """A simple class that creates a Soft Random Geometric Graph"""

    def __init__(
        self,
        number_of_nodes: int = 30,
        position_distribution: callable = np.random.uniform,
        deterrence_function: callable = lambda x: x > 0.3,
        dimension: int = 2,
        prefix: str = "node",
    ):
        nodes = [
            SpatialNode(
                name=f"{prefix}_{i}",
                geometry=Point(position_distribution(size=dimension)),
            )
            for i in range(number_of_nodes)
        ]

        edges = []
        for i in range(number_of_nodes):
            for j in range(i + 1, number_of_nodes):
                node_i = nodes[i]
                node_j = nodes[j]

                if deterrence_function(node_i["geometry"].distance(node_j["geometry"])):
                    edges.append(
                        SpatialEdge(
                            start=node_i["name"],
                            stop=node_j["name"],
                            geometry=LineString(
                                [node_i["geometry"], node_j["geometry"]]
                            ),
                        )
                    )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class RandomGeometricGraph(SoftRGG):
    """A simple class that creates a Random Geometric Graph"""

    def __init__(
        self,
        number_of_nodes: int = 200,
        radius: float = 0.1,
        position_distribution: callable = np.random.uniform,
        dimension: int = 2,
        prefix: str = "node",
    ):

        SoftRGG.__init__(
            self,
            number_of_nodes=number_of_nodes,
            position_distribution=position_distribution,
            deterrence_function=lambda x: x < (2 * radius),
            dimension=dimension,
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
        )
        # Adding the rings
        for depth in ring_depths:
            if depth > nodes_per_branch:
                raise ValueError(
                    f"Ring depth {depth} cannot be larger than Branch depth {nodes_per_branch}"
                )
            for k in range(number_of_branches):
                start_name = f"{prefix}_{depth}_{k}"
                stop_name = f"{prefix}_{depth}_{(k + 1) % number_of_branches}"

                start_node = points[start_name]
                stop_node = points[stop_name]
                arc = create_circle_arc(
                    start=start_node,
                    stop=stop_node,
                    center=points[f"{prefix}_0_0"],
                    nb_points=depth * 3,  # could be changed...
                )
                edges.append(
                    SpatialEdge(
                        start=start_name,
                        stop=stop_name,
                        geometry=arc,
                    )
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

        # generating inner lattice
        nodes, edges = generate_square_lattice_data(
            square_height=inner_square_height,
            square_width=inner_square_width,
            squares_per_line=2 * inner_semi_width,
            nb_lines=2 * inner_semi_height,
            prefix="inner",
        )

        anchors = [
            Point(-suburb_spacing, inner_semi_height * inner_square_height),  # west
            Point(
                2 * inner_semi_width * inner_square_width + suburb_spacing,
                inner_semi_height * inner_square_height,
            ),  # east
            Point(inner_semi_width * inner_square_width, -suburb_spacing),  # south
            Point(
                inner_semi_width * inner_square_width,
                2 * inner_semi_height * inner_square_height + suburb_spacing,
            ),  # north
        ]

        rotations = [270, 90, 180, 0]
        prefixes = ["west", "east", "south", "north"]

        for r, a, p in zip(rotations, anchors, prefixes):
            nodes_, edges_ = generate_regular_tree_data(
                tree_depth=suburb_depth,
                branching_factor=suburb_branching_factor,
                leaf_spacing=suburb_leaf_spacing,
                step_size=suburb_step_size,
                root=a,
                rotation=r,
                prefix=p,
            )
            nodes.extend(nodes_)
            edges.extend(edges_)

        edges.append(
            SpatialEdge(start=f"inner_{inner_semi_width}_{0}", stop=f"south_{0}_{0}")
        )

        edges.append(
            SpatialEdge(
                start=f"inner_{inner_semi_width}_{2 * inner_semi_height}",
                stop=f"north_{0}_{0}",
            )
        )

        edges.append(
            SpatialEdge(start=f"inner_{0}_{inner_semi_height}", stop=f"west_{0}_{0}")
        )

        edges.append(
            SpatialEdge(
                start=f"inner_{2 * inner_semi_width}_{inner_semi_height}",
                stop=f"east_{0}_{0}",
            )
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


if __name__ == "__main__":

    # random_spatial_graph = RandomSpatialGraph(number_of_nodes=200)
    # random_spatial_graph.draw()
    # plt.show()

    # soft_rgg = SoftRGG(number_of_nodes=200, position_distribution=np.random.normal, deterrence_function=lambda x: x < 0.3)
    # soft_rgg.draw()
    # plt.show()

    # star_network = StarSpatialGraph()
    # star_network.draw()
    # plt.show()

    star_and_ring_network = StarAndRingNetwork(
        number_of_branches=8, nodes_per_branch=6, ring_depths=[2, 5]
    )
    print(str(star_and_ring_network))
    star_and_ring_network.draw(include_names=True)
    plt.show()
