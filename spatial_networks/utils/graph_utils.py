from networkx import Graph


def merge(
    left: Graph, right: Graph, left_prefix: str = "left", right_prefix: str = "right"
):
    pass


def get_closed_triangles(graph: Graph, nodes: list = []):
    if len(nodes) == 0:
        nodes = graph.nodes
    triangles = {}

    for n in nodes:
        neighbors = graph.neighbors()
        for n1, n2 in combinations(neighbors, 2):
            if graph.has_edge(n1, n2):
                triangles[n] = triangles.get(n, []) + [(n, n1, n2)]

    return triangles


def get_open_triangles(graph: Graph, nodes: list = []):
    if len(nodes) == 0:
        nodes = graph.nodes
    triangles = {}

    for n in nodes:
        neighbors = graph.neighbors()
        for n1, n2 in combinations(neighbors, 2):
            if not graph.has_edge(n1, n2):
                triangles[n] = triangles.get(n, []) + [(n, n1, n2)]

    return triangles
