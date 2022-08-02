import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# source: https://colorpalettes.net/color-palette-4325/
DEFAULT_COLORS = {
    "nodes": "#EDC339",
    "edges": "#01577D",
    "secondary": "#227AA1",
    "background": "#D1C6BE",
}


def lp_distance(a1, a2, p=2):
    return np.power(np.sum(np.power(np.abs(a1 - a2), p), axis=-1), 1 / p)


def l2_distance(a1, a2):
    return lp_distance(a1, a2, p=2)


class SpatialNetwork(nx.Graph):
    def __init__(
        self,
        nodes: list,
        node_positions: np.array,
        edges: list,
        distance_metric: callable = l2_distance,
    ):
        # keeping nodes positions
        self.node_positions = node_positions
        self.x_positions = node_positions[:, 0]
        self.y_positions = node_positions[:, 1]
        self.node_positions_dict = {
            n: node_positions[i, :] for i, n in enumerate(nodes)
        }

        # computing distances between nodes
        edges_with_distance = []
        for e in edges:
            edges_with_distance.append(
                (
                    e[0],
                    e[1],
                    distance_metric(
                        self.node_positions_dict[e[0]], self.node_positions_dict[e[1]]
                    ),
                )
            )

        # distance
        self.distance_metric = distance_metric

        # initializing graph
        nx.Graph.__init__(self)
        nx.Graph.add_nodes_from(self, nodes)
        nx.Graph.add_weighted_edges_from(
            self, edges_with_distance, weight="distance_metric"
        )

    def compute_distance_metric(self, node1: str, node2: str):
        return self.distance_metric(
            self.node_positions_dict[node1], self.node_positions_dict[node2]
        )

    def compute_route_distance(self, node1: str, node2: str):
        try:
            return nx.shortest_path_length(
                self, source=node1, target=node2, weight="distance_metric"
            )
        except nx.NetworkXNoPath:
            return np.NaN

    def compute_distance_strength(self, node):
        s = 0
        for node2 in self.neighbors(node):
            s += self.compute_distance_metric(node, node2)
        return s

    def compute_route_factor(self, node1: str, node2: str):
        return self.compute_route_distance(node1, node2) / self.compute_distance_metric(
            node1, node2
        )

    def compute_node_accessibility(self, node: str):
        route_factors = np.array(
            [
                self.compute_route_factor(node, node2)
                for node2 in self.nodes
                if node != node2
            ]
        )
        return np.mean(route_factors[~np.isnan(route_factors)])

    def compute_graph_accessibility(self):
        node_accessibilities = np.array(
            [self.compute_node_accessibility(node) for node in self.nodes]
        )

        return np.mean(node_accessibilities[~np.isnan(node_accessibilities)])

    def elegant_draw(self):
        plt.figure(figsize=(20, 20))
        nx.draw(
            self,
            pos=self.node_positions_dict,
            node_color=DEFAULT_COLORS["nodes"],
            edge_color=DEFAULT_COLORS["edges"],
        )
        plt.xlim(-0.1, 1.1)
        plt.ylim(-0.1, 1.1)
        plt.axis("off")


class SoftRGG(SpatialNetwork):
    def __init__(
        self,
        graph_size: int,
        deterrence_function: callable,
        metric_distance: callable = l2_distance,
        dimension: int = 2,
        node_spatial_distribution: callable = np.random.uniform,
    ):

        node_positions = node_spatial_distribution(size=(graph_size, dimension))

        nodes = [i for i in range(graph_size)]

        self.metric_distances = {
            (i, j): metric_distance(node_positions[i], node_positions[j])
            for i in range(graph_size)
            for j in range(i + 1, graph_size)
        }
        edges = []

        for (i, j), distance in self.metric_distances.items():
            if np.random.uniform() < deterrence_function(distance):
                edges.append((i, j))
        SpatialNetwork.__init__(
            self, nodes=nodes, node_positions=node_positions, edges=edges
        )

        self.deterrence_function = deterrence_function
        self.node_spatial_distribution = node_spatial_distribution
        self.dimension = dimension


class RandomGeometricGraph(SoftRGG):
    def __init__(
        self,
        graph_size: int,
        radius: float,
        dimension: int = 2,
        metric_distance: callable = l2_distance,
        node_spatial_distribution: callable = np.random.uniform,
    ):
        def deterrence_function(d):
            return 1 if d < radius * 2 else 0

        self.radius = radius

        SoftRGG.__init__(
            self,
            graph_size=graph_size,
            deterrence_function=deterrence_function,
            metric_distance=metric_distance,
            dimension=dimension,
            node_spatial_distribution=node_spatial_distribution,
        )


class StarNetwork(SpatialNetwork):
    def __init__(self, number_of_branches=6, branch_length=11):
        node_positions = np.array(
            [(0, 0)]
            + [
                (
                    r * np.sin(2 * np.pi * k / number_of_branches),
                    r * np.cos(2 * np.pi * k / number_of_branches),
                )
                for r in range(1, branch_length)
                for k in range(number_of_branches)
            ]
        )
        node_positions = node_positions / (2 * node_positions.max()) + 0.5

        edges = [(0, i) for i in range(1, number_of_branches + 1)]
        for i in range(1, len(a.nodes) - number_of_branches):
            edges.append((i, i + number_of_branches))
        SpatialNetwork.__init__(
            self,
            nodes=range(len(node_positions)),
            node_positions=node_positions,
            edges=edges,
        )


class StarAndRingNetwork(SpatialNetwork):
    def __init__(self, number_of_branches=6, branch_length=11, ring_depth=4):

        if ring_depth > branch_length:
            raise ValueError(
                f"'ring_depth' {ring_depth} cannot be larger than 'branch_length' {branch_length}"
            )
        node_positions = np.array(
            [(0, 0)]
            + [
                (
                    r * np.sin(2 * np.pi * k / number_of_branches),
                    r * np.cos(2 * np.pi * k / number_of_branches),
                )
                for r in range(1, branch_length)
                for k in range(number_of_branches)
            ]
        )
        node_positions = node_positions / (2 * node_positions.max()) + 0.5

        edges = [(0, i) for i in range(1, number_of_branches + 1)]
        for i in range(1, len(a.nodes) - number_of_branches):
            edges.append((i, i + number_of_branches))

        for i in range(number_of_branches):
            edges.append(
                (
                    ring_depth * number_of_branches + 1 + i,
                    ring_depth * number_of_branches + 1 + (i + 1) % number_of_branches,
                )
            )

        SpatialNetwork.__init__(
            self,
            nodes=range(len(node_positions)),
            node_positions=node_positions,
            edges=edges,
        )


if __name__ == "__main__":

    # Testing out LP distance

    a1 = np.array([[0, 0], [1, 1]])
    a2 = np.array([[0, 1], [0, 0]])

    print(lp_distance(a1, a2, 1))
    print(lp_distance(a1, a2, 2))

    # Testing out RGG
    my_graph = RandomGeometricGraph(graph_size=30, radius=0.1)
    my_graph.elegant_draw()
    plt.show()

    print(my_graph.compute_graph_accessibility())
