import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon

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
    check_edge,
    check_node,
    create_circle_arc,
    generate_star_spatial_network_data,
    generate_square_lattice_data,
    generate_triangle_lattice_data,
    generate_hexagonal_lattice_data,
    SpatialEdge,
    SpatialNode,
)

# import warnings

# warnings.filterwarnings("error")


class SpatialGraph(Graph):
    """Class that represents a Spatial Graphs"""

    def __init__(self, nodes: list = [], edges: list = []):
        """SpatialGraph constructor

        Args:
            nodes (list, optional): list of nodes of the Spatial Graph.
            Nodes should be of the SpatialNode class or dictionaries with
            "name" (str) and "geometry"(shapely.geometry.Point) keys
            Defaults to [].
            edges (list, optional): list of edges of the Spatial Graph.
            Edges should be of the SpatialEdge class or dictionaries with
            "start" (str), "end" (str) and "geometry" (shapely.geometry.LineString)
            Defaults to [].

        Raises:
            ValueError: A ValueError can be raised if geometry attribute
                of nodes are not of the same dimension
            ValueError: A ValueError can be raised if "geometry" or "name"
                are not attributes of a Node
            ValueError: A ValueError can be raised if "start", "end" or "geometry"
                are not attributes of an Edge
            TypeError: A TypeError can be raised if the "geometry" attribute of a Node
                is not of the shapely.geometry.Point class
            TypeError: A TypeError can be raised if the "geometry" attribute of an Edge
                is not of the shapely.geometry.LineString class

        """
        Graph.__init__(self=self)
        self.node_properties = {}
        self.edge_properties = {}

        dimensions = []
        for n in nodes:
            self.add_node(n)
            dimensions.append(n["geometry"].has_z)

        if sum(dimensions) == 1:
            self.dimension = 3
        elif sum(dimensions) == 0:
            self.dimension = 2
        else:
            raise ValueError("Nodes are not all of the same dimension")

        self.node_properties = {n["name"]: n for n in nodes}
        self.edge_properties = {}

        for e in edges:
            self.add_edge(e)
            self.edge_properties[(e["start"], e["end"])] = e

    def add_node(self, node_to_add):
        node = check_node(node=node_to_add)
        Graph.add_node(self, node_for_adding=node["name"], **node)
        self.node_properties[node["name"]] = {**node}

    def add_edge(self, edge_to_add):
        edge = check_edge(edge=edge_to_add, nodes_dict=self.node_properties)
        Graph.add_edge(self, u_of_edge=edge["start"], v_of_edge=edge["end"], **edge)
        self.edge_properties[(edge["start"], edge["end"])] = {**edge}

    def draw_nodes(
        self, node_color="#EDC339", node_size=100, include_names=False, ax=None
    ):
        if not ax:
            fig, ax = plt.subplots(1, 1)
        xs, ys = [], []
        for n in self.node_properties:
            xs.append(self.node_properties[n]["geometry"].x)
            ys.append(self.node_properties[n]["geometry"].y)

        ax.scatter(xs, ys, color=node_color, s=node_size)

        if include_names:
            for n in self.node_properties:
                node = self.node_properties[n]
                ax.annotate(text=node["name"], xy=node["geometry"].coords[0])
        return ax

    def draw_edges(self, edge_color="#01577D", ax=None):
        if not ax:
            fig, ax = plt.subplots(1, 1)
        for e in self.edges:
            coordinates = np.asarray(self.edges[e]["geometry"].coords)
            ax.plot(coordinates[:, 0], coordinates[:, 1], color=edge_color, zorder=-1)
        return ax

    def draw(self, include_names=False, ax=None):

        if not ax:
            fig, ax = plt.subplots(1, 1)
        self.draw_edges(ax=ax)
        self.draw_nodes(ax=ax, include_names=include_names)
        return ax

    def add_edges_from(self, edges_to_add):
        for e in edges_to_add:
            self.add_edge(e)

    def add_nodes_from(self, nodes_to_add):
        for n in nodes_to_add:
            self.add_node(n)

    def remove_edge(self, edge_to_remove):
        e = (edge_to_remove["start"], edge_to_remove["end"])
        self.edge_properties.remove(e)
        Graph.remove_edge(self, e[0], e[1])

    def remove_node(self, node_to_remove):
        n = node_to_remove["name"]
        Graph.remove_node(self, n)
        self.node_properties.pop(n)

    def remove_edges_from(self, edges_to_remove):
        for e in edges_to_remove:
            self.remove_edge(edge_to_remove=e)

    def remove_nodes_from(self, nodes_to_remove):
        for n in nodes_to_remove:
            self.remove_node(node_to_remove=n)

    def route_distance(self, node_i_name: str, node_j_name: str):
        try:
            return nx.shortest_path_length(
                self, source=node_i_name, target=node_j_name, weight="length"
            )
        except nx.NetworkXNoPath:
            return np.NaN

    def metric_distance(self, node_i_name: str, node_j_name: str):
        node_i = self.node_properties[node_i_name]
        node_j = self.node_properties[node_j_name]

        return node_i["geometry"].distance(node_j["geometry"])

    def detour_index(self, node_i_name: str, node_j_name: str):
        return self.route_distance(node_i_name, node_j_name) / self.metric_distance(
            node_i_name, node_j_name
        )


class RandomSpatialGraph(SpatialGraph):
    """A simple class that creates a Random Graph with random positions"""

    def __init__(
        self,
        number_of_nodes: int = 200,
        edge_probability: float = 0.01,
        dimension: int = 2,
        position_distribution: callable = np.random.uniform,
    ):
        if dimension not in [2, 3]:
            raise ValueError(f"dimension should be 2 or 3 not '{dimention}'")

        nodes = [
            SpatialNode(
                name=f"node_{i}", geometry=Point(position_distribution(size=dimension))
            )
            for i in range(number_of_nodes)
        ]

        edges = []

        for i in range(number_of_nodes):
            for j in range(i + 1, number_of_nodes):
                if np.random.uniform() < edge_probability:
                    edges.append(
                        SpatialEdge(
                            start=f"node_{i}",
                            end=f"node_{j}",
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
    ):
        nodes = [
            SpatialNode(
                name=f"node_{i}", geometry=Point(position_distribution(size=dimension))
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
                            end=node_j["name"],
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

    def __init__(self, number_of_branches: int = 6, nodes_per_branch: int = 10):

        _, nodes, edges = generate_star_spatial_network_data(
            number_of_branches=number_of_branches, nodes_per_branch=nodes_per_branch
        )

        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class StarAndRingNetwork(SpatialGraph):
    def __init__(
        self,
        number_of_branches: int = 6,
        nodes_per_branch: int = 10,
        ring_depths: list = [5],
    ):
        # building the star network
        points, nodes, edges = generate_star_spatial_network_data(
            number_of_branches=number_of_branches, nodes_per_branch=nodes_per_branch
        )
        # Adding the rings
        for depth in ring_depths:
            if depth > nodes_per_branch:
                raise ValueError(
                    f"Ring depth {depth} cannot be larger than Branch depth {nodes_per_branch}"
                )
            for k in range(number_of_branches):
                start_name = f"node_{depth}_{k}"
                end_name = f"node_{depth}_{(k + 1) % number_of_branches}"

                start_node = points[start_name]
                end_node = points[end_name]
                arc = create_circle_arc(
                    start=start_node,
                    end=end_node,
                    center=points["node_0_0"],
                    nb_points=depth * 3,  # could be changed...
                )
                edges.append(
                    SpatialEdge(
                        start=start_name,
                        end=end_name,
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
    ):
        nodes, edges = generate_square_lattice_data(
            nb_lines=nb_lines,
            squares_per_line=squares_per_line,
            square_height=square_height,
            square_width=square_width,
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
    ):
        nodes, edges = generate_triangle_lattice_data(
            nb_lines=nb_lines,
            triangles_per_line=triangles_per_line,
            triangle_base=triangle_base,
            triangle_height=triangle_height,
        )
        SpatialGraph.__init__(self, nodes=nodes, edges=edges)


class HexagonalLattice(SpatialGraph):
    """A regular hexagonal lattice"""

    def __init__(
        self, hexagons_per_line: int = 3, nb_lines: int = 4, hexagon_base: int = 1.0
    ):
        nodes, edges = generate_hexagonal_lattice_data(
            hexagons_per_line=hexagons_per_line,
            nb_lines=nb_lines,
            hexagon_base=hexagon_base,
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
