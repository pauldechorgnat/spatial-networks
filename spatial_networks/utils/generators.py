import numpy as np

from itertools import combinations

from shapely.geometry import Point
from shapely.geometry import LineString

from .core_utils import SpatialEdge
from .core_utils import SpatialNode
from .geometry_utils import create_circle_arc


def generate_soft_rgg_data(
    n_nodes: int = 40,
    position_distribution: callable = np.random.uniform,
    deterrence_function: callable = lambda x: x < 0.5,
    prefix: str = "soft_rgg",
):
    """Generates nodes and edges for a Soft RGG.

    Args:
        n_nodes (int, optional): number of nodes to generate.
            Defaults to 40.
        position_distribution (callable, optional): distribution of the position of the nodes.
            This function should be able to take a tuple for `size` argument.
            Defaults to np.random.uniform.
        deterrence_function (_type_, optional): function to determine if an edge should be built between two nodes.
            This function takes the distance between two nodes as sole argument.
            Defaults to lambda x:x<0.5.
        prefix (str, optional): prefix used to name nodes.
            Defaults to "soft_rgg".

    Returns:
        tuple(nodes, edges): a list of SpatialNode and a list of SpatialEdge
    """
    positions = position_distribution(size=(n_nodes, 2))
    nodes = [
        SpatialNode(name=f"{prefix}_{i}", geometry=Point(positions[i]))
        for i in range(n_nodes)
    ]

    edges = []

    for node_i, node_j in combinations(nodes, r=2):
        distance = node_i["geometry"].distance(node_j["geometry"])
        if deterrence_function(distance):
            edges.append(SpatialEdge(start=node_i["name"], stop=node_j["name"]))
    return nodes, edges


def generate_star_spatial_network_data(
    number_of_branches: int = 6,
    nodes_per_branch: int = 6,
    prefix: str = "star",
    ring_depths: list = [],
):
    """Generates nodes and edges for a star SpatialGraph

    Args:
        number_of_branches (int, optional): Number of branches in the star.
            Defaults to 6.
        nodes_per_branch (int, optional): depth of the star.
        Defaults to 6.
        ring_depths (list, optional): depth of rings to add to the tree.
            Defaults to [].
        prefix (str, optional): prefix used to name nodes.
            Defaults to "star".

    Returns:
        tuple(nodes, edges): a list of SpatialNode and a list of SpatialEdge
    """
    points = {
        f"{prefix}_0_0": Point([0, 0]),
        **{
            f"{prefix}_{r}_{k}": Point(
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
                start=f"{prefix}_0_0",
                stop=f"{prefix}_1_{k}",
                geometry=LineString(
                    [points[f"{prefix}_0_0"], points[f"{prefix}_1_{k}"]]
                ),
            )
        )
    # branches
    for r in range(1, nodes_per_branch - 1):
        for k in range(number_of_branches):
            node_start = f"{prefix}_{r}_{k}"
            node_stop = f"{prefix}_{r + 1}_{k}"
            edges.append(
                SpatialEdge(
                    start=node_start,
                    stop=node_stop,
                    geometry=LineString([points[node_start], points[node_stop]]),
                )
            )
    for depth in ring_depths:
        if (depth > nodes_per_branch) or (depth == 0):
            raise ValueError(
                f"Ring depth {depth} cannot be larger than nodes_per_branch {nodes_per_branch} or 0"
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
    return points, nodes, edges


def generate_square_lattice_data(
    square_width: float = 0.5,
    square_height: float = 0.5,
    squares_per_line: int = 5,
    nb_lines: int = 5,
    prefix: str = "square",
):
    """Generates nodes and edges for a squared lattice SpatialGraph

    Args:
        square_width (float, optional): horizontal width of each rectangle.
            Defaults to 0.5.
        square_height (float, optional): vertical height of each rectangle.
            Defaults to 0.5.
        squares_per_line (int, optional): horizontal number of squares in the lattice.
            Defaults to 5.
        nb_lines (int, optional): vertical number of squares in the lattice.
            Defaults to 5.
        prefix (str, optional): prefix used to name nodes.
            Defaults to "square".

    Returns:
        tuple(nodes, edges): a list of SpatialNode and a list of SpatialEdge
    """
    lattice_height = nb_lines + 1
    lattice_width = squares_per_line + 1
    nodes = [
        SpatialNode(
            name=f"{prefix}_{w}_{h}",
            geometry=Point(w * square_width, h * square_height),
        )
        for w in range(lattice_width)
        for h in range(lattice_height)
    ]

    edges = [
        SpatialEdge(
            start=f"{prefix}_{w}_{h}",
            stop=f"{prefix}_{w}_{h + 1}",
        )
        for h in range(lattice_height - 1)
        for w in range(lattice_width)
    ] + [
        SpatialEdge(
            start=f"{prefix}_{w}_{h}",
            stop=f"{prefix}_{w + 1}_{h}",
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
    prefix: str = "triangle",
):
    """Generates nodes and edges for a triangle lattice SpatialGraph

    Args:
        nb_lines (int, optional): vertical number of triangles in the lattice.
            Defaults to 6.
        triangles_per_line (int, optional): horizontal number of triangles in the lattice.
            Defaults to 5.
        triangle_base (float, optional): horizontal base of the triangles.
            Defaults to 1.0.
        triangle_height (float, optional): vertical height of the triangles.
            Defaults to 1.0.
        prefix (str, optional): prefix used to name nodes.
            Defaults to "triangle".

    Returns:
        tuple(nodes, edges): a list of SpatialNode and a list of SpatialEdge
    """
    lattice_width = triangles_per_line + 1
    lattice_height = nb_lines + 1
    nodes = [
        SpatialNode(
            name=f"{prefix}_{w}_{h}",
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
                start=f"{prefix}_{w}_{h}",
                stop=f"{prefix}_{w}_{h + 1}",
            )
            for h in range(lattice_height - 1)
            for w in range(lattice_width)
        ]
        + [
            SpatialEdge(
                start=f"{prefix}_{w}_{h}",
                stop=f"{prefix}_{w + 1}_{h}",
            )
            for h in range(lattice_height)
            for w in range(lattice_width - 1)
        ]
        + [
            SpatialEdge(
                start=f"{prefix}_{w}_{h}",
                stop=f"{prefix}_{w + 1}_{h + 1}",
            )
            for h in range(1, lattice_height - 1, 2)
            for w in range(lattice_width - 1)
        ]
        + [
            SpatialEdge(
                start=f"{prefix}_{w}_{h}",
                stop=f"{prefix}_{w - 1}_{h + 1}",
            )
            for h in range(0, lattice_height - 1, 2)
            for w in range(1, lattice_width)
        ]
    )

    return nodes, edges


def generate_hexagonal_lattice_data(
    hexagons_per_line: int = 3,
    nb_lines: int = 4,
    hexagon_base: int = 1.0,
    prefix: str = "hexagon",
):
    """Generates nodes and edges for a hexagonal lattice SpatialGraph

    Args:
        hexagons_per_line (int, optional): horizontal number of hexagons in the lattice.
            Defaults to 3.
        nb_lines (int, optional): vertical number of hexagons in the lattice.
            Defaults to 4.
        hexagon_base (int, optional): side of hexagons in the lattice.
            Defaults to 1.0.
        prefix (str, optional): prefix used to name nodes.
            Defaults to "hexagon".

    Returns:
        tuple(nodes, edges): a list of SpatialNode and a list of SpatialEdge
    """
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
            node_name = f"{prefix}_{i}_{j}"
            nodes_dict[node_name] = SpatialNode(
                name=node_name,
                geometry=Point(
                    0.5 * hexagon_base
                    + (i + i // 2) * hexagon_base
                    + (j % 2) * ((i % 2) - 0.5) * hexagon_base,
                    half_height * j,
                ),
            )

    nodes_dict.pop(f"{prefix}_0_{M + 1}")
    nodes_dict.pop(f"{prefix}_{n}_{(M + 1) * (n % 2)}")

    for i in cols:
        for j in rows[: M + 1]:
            start_name = f"{prefix}_{i}_{j}"
            stop_name = f"{prefix}_{i}_{j + 1}"
            if (start_name in nodes_dict) and (stop_name in nodes_dict):
                edges.append(SpatialEdge(start=start_name, stop=stop_name))

    for i in cols[:n]:
        for j in rows:
            start_name = f"{prefix}_{i}_{j}"
            stop_name = f"{prefix}_{i + 1}_{j}"
            if (
                (start_name in nodes_dict)
                and (stop_name in nodes_dict)
                and (i % 2 == j % 2)
            ):
                edges.append(SpatialEdge(start=start_name, stop=stop_name))
    nodes = nodes_dict.values()

    return nodes, edges


def generate_regular_tree_data(
    branching_factor: int = 3,
    tree_depth: int = 4,
    leaf_spacing: float = 1.0,
    step_size: list = 1.0,
    root: Point = Point(0, 0),
    rotation=0,
    prefix: str = "tree",
):
    """Generates nodes and edges for a regular tree SpatialGraph

    Args:
        branching_factor (int, optional): number of children per step.
            Defaults to 3.
        tree_depth (int, optional): depth of the tree.
            A graph with a single node is a tree of depth 0.
            Defaults to 4.
        leaf_spacing (float, optional): space between leaves (final depth).
            Defaults to 1.0.
        step_size (list, optional): distance between different depths.
            This argument can be a list of numerical values or a single numerical value.
            Defaults to 1.0.
        root (Point, optional): position of the root of the tree.
            Defaults to Point(0, 0).
        rotation (int, optional): rotation angle of the graph in degrees.
            Defaults to 0.
        prefix (str, optional): prefix used to name nodes.
            Defaults to "tree".

    Raises:
        ValueError: if `step_size` is a list of size different from tree_depth
        TypeError: if `step_size` is neither a list or a numerical value

    Returns:
        tuple(nodes, edges): a list of SpatialNode and a list of SpatialEdge
    """
    if (isinstance(step_size, float)) or (isinstance(step_size, int)):
        step_sizes = np.arange(1, tree_depth + 1) * step_size
    elif isinstance(step_size, list):
        if len(step_size) != tree_depth:
            raise ValueError(
                f"`step_size` should be a list with a size of `tree_depth`= {tree_depth}"
            )
        step_sizes = step_size

    else:
        raise TypeError(
            "`step_size` should be a list or a numerical value. "
            f"Received `{type(step_size)}`"
        )

    x_root, y_root = root.x, root.y

    nodes, edges = [SpatialNode(name=f"{prefix}_0_0", geometry=root)], []

    final_width = (branching_factor ** (tree_depth)) * leaf_spacing

    cos = np.cos(rotation * 2 * np.pi / 360)
    sin = np.sin(rotation * 2 * np.pi / 360)

    for d in range(1, tree_depth + 1):

        current_width = final_width - final_width / (branching_factor**d)
        number_of_nodes = branching_factor**d
        s = step_sizes[d - 1]
        for n in range(0, number_of_nodes):

            x_delta = -(current_width / 2) + (current_width * n / (number_of_nodes - 1))
            y_delta = s

            x = x_root + cos * x_delta + sin * y_delta
            y = y_root - sin * x_delta + cos * y_delta

            nodes.append(SpatialNode(name=f"{prefix}_{d}_{n}", geometry=Point(x, y)))

            if d > 0:
                edges.append(
                    SpatialEdge(
                        start=f"{prefix}_{d - 1}_{n // branching_factor}",
                        stop=f"{prefix}_{d}_{n}",
                    )
                )

    return nodes, edges


def generate_circular_tree_data(
    branching_factor: int = 4,
    tree_depth: int = 3,
    step_size: list = 1,
    ring_depths: list = [],
    prefix: str = "circular_tree",
    root: Point = Point(0, 0),
):
    """Generates nodes and edges for a circular tree SpatialGraph

    Args:
        branching_factor (int, optional): number of children per step.
            Defaults to 4.
        tree_depth (int, optional): depth of the tree.
            Defaults to 3.
        step_size (list, optional): distance between different depths.
            This argument can be a list of numerical values or a single numerical value.
            Defaults to 1.0.
        root (Point, optional): position of the root of the tree.
            Defaults to Point(0, 0).
        ring_depths (list, optional): depth of rings to add to the tree.
            Defaults to [].
        prefix (str, optional): prefix used to name nodes.
            Defaults to "circular_tree".

    Raises:
        ValueError: if `step_size` is a list of size different from tree_depth
        TypeError: if `step_size` is neither a list or a numerical value
        ValueError: if one of the `ring_depths` value is not valid

    Returns:
        tuple(nodes, edges): a list of SpatialNode and a list of SpatialEdge
    """
    if (isinstance(step_size, float)) or (isinstance(step_size, int)):
        step_sizes = np.arange(1, tree_depth + 1) * step_size
    elif isinstance(step_size, list):
        if len(step_size) != tree_depth:
            raise ValueError(
                f"`step_size` should be a list with a size of `tree_depth`= {tree_depth}"
            )
        step_sizes = step_size

    else:
        raise TypeError(
            "`step_size` should be a list or a numerical value. "
            f"Received `{type(step_size)}`"
        )
    nodes = [SpatialNode(name=f"{prefix}_0_0", geometry=root)]

    edges = []

    x_root, y_root = root.x, root.y

    for d in range(1, tree_depth + 1):
        depth = step_sizes[d - 1]
        number_of_nodes = branching_factor**d

        offset = 2 * np.pi / number_of_nodes * (branching_factor ** (d - 1) - 1) / 2

        for n in range(number_of_nodes):

            nodes.append(
                SpatialNode(
                    name=f"{prefix}_{d}_{n}",
                    geometry=Point(
                        x_root
                        + depth * np.cos(2 * np.pi * n / number_of_nodes - offset),
                        y_root
                        + depth * np.sin(2 * np.pi * n / number_of_nodes - offset),
                    ),
                )
            )
            if n != number_of_nodes:
                edges.append(
                    SpatialEdge(
                        start=f"{prefix}_{d-1}_{(n) // branching_factor}",
                        stop=f"{prefix}_{d}_{n}",
                    )
                )
    for d in ring_depths:
        if (d == 0) or (d > tree_depth):
            raise ValueError(
                f"`ring_depths` cannot be 0 or larger than `tree_depth={tree_depth}`. Received {d}"
            )
        number_of_nodes = branching_factor**d
        edges.extend(
            [
                SpatialEdge(
                    start=f"{prefix}_{d}_{n}",
                    stop=f"{prefix}_{d}_{(n + 1) % number_of_nodes}",
                )
                for n in range(number_of_nodes)
            ]
        )

    return nodes, edges


def generate_grid_tree_data(
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

    return nodes, edges
