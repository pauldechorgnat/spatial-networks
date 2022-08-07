import numpy as np

from shapely.geometry import Point
from shapely.geometry import LineString

from .core_utils import SpatialEdge
from .core_utils import SpatialNode


def generate_random_graph_data(
    n_nodes: int = 40,
    edge_probability: float = 0.01,
    position_distribution: callable = np.random.uniform,
    dimension: int = 2,
):
    nodes = [
        SpatialNode(
            name=f"node_{i}", geometry=Point(position_distribution(size=dimension))
        )
        for i in range(n_nodes)
    ]

    edges = []

    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if np.random.uniform() < edge_probability:
                edges.append(
                    SpatialEdge(
                        start=nodes[i]["name"],
                        end=nodes[j]["name"],
                        geometry=LineString(
                            [nodes[i]["geometry"], nodes[j]["geometry"]]
                        ),
                    )
                )

    return nodes, edges


def generate_star_spatial_network_data(
    number_of_branches: int = 6, nodes_per_branch: int = 6
):
    points = {
        "node_0_0": Point([0, 0]),
        **{
            f"node_{r}_{k}": Point(
                (
                    r * np.cos(2 * np.pi * k / number_of_branches + np.pi / 2),
                    r * np.sin(2 * np.pi * k / number_of_branches + np.pi / 2),
                )
            )
            for r in range(1, nodes_per_branch)
            for k in range(number_of_branches)
        },
    }
    nodes = [SpatialNode(name=p, geometry=points[p]) for p in points]
    edges = []
    # first ring
    for k in range(number_of_branches):
        edges.append(
            SpatialEdge(
                start="node_0_0",
                end=f"node_1_{k}",
                geometry=LineString([points["node_0_0"], points[f"node_1_{k}"]]),
            )
        )
    # branches
    # for i in range(1, 1 + number_of_branches * nodes_per_branch - number_of_branches):
    for r in range(1, nodes_per_branch - 1):
        for k in range(number_of_branches):
            node_start = f"node_{r}_{k}"
            node_end = f"node_{r + 1}_{k}"
            edges.append(
                SpatialEdge(
                    start=node_start,
                    end=node_end,
                    geometry=LineString([points[node_start], points[node_end]]),
                )
            )
    return points, nodes, edges


def generate_square_lattice_data(
    square_width: float = 0.5,
    square_height: float = 0.5,
    squares_per_line: int = 5,
    nb_lines: int = 5,
):
    lattice_height = nb_lines + 1
    lattice_width = squares_per_line + 1
    nodes = [
        SpatialNode(
            name=f"node_{w}_{h}", geometry=Point(w * square_width, h * square_height)
        )
        for w in range(lattice_width)
        for h in range(lattice_height)
    ]

    edges = [
        SpatialEdge(
            start=f"node_{w}_{h}",
            end=f"node_{w}_{h + 1}",
        )
        for h in range(lattice_height - 1)
        for w in range(lattice_width)
    ] + [
        SpatialEdge(
            start=f"node_{w}_{h}",
            end=f"node_{w + 1}_{h}",
        )
        for h in range(lattice_height)
        for w in range(lattice_width - 1)
    ]

    return nodes, edges


def generate_triangle_lattice_data(
    nb_lines: int = 6,
    triangles_per_line: int = 5,
    triangle_base: float = 1.0,
    triangle_height: float = 1.0,
):
    lattice_width = triangles_per_line + 1
    lattice_height = nb_lines + 1
    nodes = [
        SpatialNode(
            name=f"node_{w}_{h}",
            geometry=Point(
                w * triangle_base + (0.5 * triangle_base if h % 2 == 1 else 0),
                h * triangle_height,
            ),
        )
        for w in range(lattice_width)
        for h in range(lattice_height)
    ]
    edges = (
        [
            SpatialEdge(
                start=f"node_{w}_{h}",
                end=f"node_{w}_{h + 1}",
            )
            for h in range(lattice_height - 1)
            for w in range(lattice_width)
        ]
        + [
            SpatialEdge(
                start=f"node_{w}_{h}",
                end=f"node_{w + 1}_{h}",
            )
            for h in range(lattice_height)
            for w in range(lattice_width - 1)
        ]
        + [
            SpatialEdge(
                start=f"node_{w}_{h}",
                end=f"node_{w + 1}_{h + 1}",
            )
            for h in range(1, lattice_height - 1, 2)
            for w in range(lattice_width - 1)
        ]
        + [
            SpatialEdge(
                start=f"node_{w}_{h}",
                end=f"node_{w - 1}_{h + 1}",
            )
            for h in range(0, lattice_height - 1, 2)
            for w in range(1, lattice_width)
        ]
    )

    return nodes, edges


def generate_hexagonal_lattice_data(
    hexagons_per_line: int = 3, nb_lines: int = 4, hexagon_base: int = 1.0
):
    half_height = np.sqrt(3) / 2 * hexagon_base
    small_width = hexagon_base / 2
    nodes, edges = [], []
    half_height = np.sqrt(3) / 2 * hexagon_base

    small_width = hexagon_base / 2
    nodes, edges = [], []

    M = 2 * nb_lines
    n = hexagons_per_line

    rows = range(M + 2)
    cols = range(n + 1)

    nodes_dict = {}

    for i in cols:
        for j in rows:
            node_name = f"node_{i}_{j}"
            nodes_dict[node_name] = SpatialNode(
                name=node_name,
                geometry=Point(
                    0.5 * hexagon_base
                    + (i + i // 2) * hexagon_base
                    + (j % 2) * ((i % 2) - 0.5) * hexagon_base,
                    half_height * j,
                ),
            )

    nodes_dict.pop(f"node_0_{M + 1}")
    nodes_dict.pop(f"node_{n}_{(M + 1) * (n % 2)}")

    for i in cols:
        for j in rows[: M + 1]:
            start_name = f"node_{i}_{j}"
            end_name = f"node_{i}_{j + 1}"
            if (start_name in nodes_dict) and (end_name in nodes_dict):
                edges.append(SpatialEdge(start=start_name, end=end_name))

    for i in cols[:n]:
        for j in rows:
            start_name = f"node_{i}_{j}"
            end_name = f"node_{i + 1}_{j}"
            if (
                (start_name in nodes_dict)
                and (end_name in nodes_dict)
                and (i % 2 == j % 2)
            ):
                edges.append(SpatialEdge(start=start_name, end=end_name))
    nodes = nodes_dict.values()

    return nodes, edges
