"""
Contains basic data structures:

- SpatialNode
- SpatialEdge
- SpatialGraph
"""

from collections.abc import Mapping
from collections.abc import Hashable

import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPoint
from networkx import Graph
from networkx import MultiGraph


class SpatialNode(Mapping):
    """Class to implement Nodes in Spatial Graphs"""

    def __init__(self, name: Hashable, geometry: Point, **attr):
        """Constructor of a SpatialNode

        Args:
            name (Hashable): name of the node
            geometry (Point): location of the node
            **attr: any other attribute of the node

        Raises:
            TypeError: if `name` is not a Hashable object or `name` is None
            TypeError: if `geometry` is not shapely.geometry.Point object
            ValueError: if `geometry` is a three-dimension shapely.geometry.Point
        """
        self._check_name(name=name)
        self._check_geometry(geometry=geometry)

        self.name = name
        self.geometry = geometry
        self.attributes = {**attr, **{"name": name, "geometry": geometry}}

    def _check_name(self, name):
        if (name is None) or (not isinstance(name, Hashable)):
            raise TypeError(
                "'name' should be a hashable object which is not None. "
                f"Received a '{type(name)}' object"
            )

    def _check_geometry(self, geometry):
        if not isinstance(geometry, Point):
            raise TypeError(
                "'geometry' should be a shapely.geometry.Point object. "
                f"Received a '{type(geometry)}' object."
            )
        if geometry.has_z:
            raise ValueError("'geometry' should be a two-dimension object.")

    def __getitem__(self, attr_name):
        return self.attributes[attr_name]

    def __contains__(self, attr_name):
        return attr_name in self.attributes

    def __len__(self):
        return len(self.attributes)

    def __iter__(self):
        return iter(self.attributes)

    def __setitem__(self, attr_name, attr_value):
        if attr_name == "name":
            self._check_name(name=attr_value)
            self.name = attr_value
        elif attr_name == "geometry":
            self._check_geometry(attr_value)
            self.geometry = attr_value
        self.attributes[attr_name] = attr_value

    def __str__(self):
        return f"SpatialNode '{self.name}' with coordinates: {self.geometry}"


class SpatialEdge(Mapping):
    """Class to implement Edges in Spatial Graphs"""

    def __init__(
        self, start: Hashable, stop: Hashable, geometry: LineString = None, **attr
    ):
        """Constructor of a SpatialEdge

        Args:
            start (Hashable): name of the starting node of the edge
            stop (Hashable): name of the end node of the edge
            geometry (LineString, optional): shape of the edge.
                If not specified, the geometry will be assumed to be a straight line from `start` to `end`.
                Defaults to None.
            **attr: any other attribute of the edge. Cannot be `key`.

        Raises:
            TypeError: if `start` is not a Hashable object or `name` is None.
            TypeError: if `stop` is not a Hashable object or `name` is None.
            TypeError: if `geometry` is not None or a shapely.geometry.LineString object.
            ValueError: if `key` passed in the constructor
        """
        self._check_start(start=start)
        self._check_stop(stop=stop)
        self._check_geometry(geometry=geometry)
        self._check_attributes(attributes=attr)
        self.start = start
        self.stop = stop
        self.geometry = geometry
        self.attributes = {
            **attr,
            **{"start": start, "stop": stop, "geometry": geometry},
        }

    def __getitem__(self, attr_name):
        return self.attributes[attr_name]

    def __contains__(self, attr_name):
        return attr_name in self.attributes

    def __len__(self):
        return len(self.attributes)

    def __iter__(self):
        return iter(self.attributes)

    def __setitem__(self, attr_name, attr_value):
        self._check_attributes(attributes=[attr_name])
        if attr_name == "start":
            self._check_start(start=attr_value)
            self.start = attr_value
        elif attr_name == "stop":
            self._check_stop(stop=attr_value)
            self.stop = attr_value
        elif attr_name == "geometry":
            self._check_geometry(geometry=attr_value)

        self.attributes[attr_name] = attr_value

    def __str__(self):
        return f"SpatialEdge from node '{self.start}' to node '{self.stop}'"

    def _check_start(self, start):
        if (start is None) or (not isinstance(start, Hashable)):
            raise TypeError(
                "'start' should be a hashable object which is not None. "
                f"Received a '{type(start)}' object"
            )

    def _check_stop(self, stop):
        if (stop is None) or (not isinstance(stop, Hashable)):
            raise TypeError(
                "'stop' should be a hashable object which is not None. "
                f"Received a '{type(stop)}' object"
            )

    def _check_geometry(self, geometry):
        if (geometry is not None) and (not isinstance(geometry, LineString)):
            raise TypeError(
                "'geometry' should be a shapely.geometry.LineString object or None. "
                f"Received a '{type(geometry)}' object."
            )

    def _check_attributes(self, attributes):
        if "key" in attributes:
            raise ValueError("'key' cannot be an attribute of a SpatialEdge")


class SpatialGraph(MultiGraph):
    """Class that represents a Spatial Graphs"""

    def __init__(self, nodes: list = [], edges: list = []):
        """SpatialGraph constructor

        Args:
            nodes (list, optional): list of nodes of the Spatial MultiGraph.
            Nodes should be of the SpatialNode class or dictionaries with
            "name" (str) and "geometry"(shapely.geometry.Point) keys
            Defaults to [].
            edges (list, optional): list of edges of the Spatial MultiGraph.
            Edges should be of the SpatialEdge class or dictionaries with
            "start" (str), "stop" (str) and "geometry" (shapely.geometry.LineString)
            Defaults to [].

        Raises:
            ValueError: A ValueError can be raised if geometry attribute
                of nodes are not of the same dimension
            ValueError: A ValueError can be raised if "geometry" or "name"
                are not attributes of a Node
            ValueError: A ValueError can be raised if "start", "stop" or "geometry"
                are not attributes of an Edge
            TypeError: A TypeError can be raised if the "geometry" attribute of a Node
                is not of the shapely.geometry.Point class
            TypeError: A TypeError can be raised if the "geometry" attribute of an Edge
                is not of the shapely.geometry.LineString class

        """
        MultiGraph.__init__(self=self)

        self.add_nodes_from(nodes_to_add=nodes)
        self.add_edges_from(edges_to_add=edges)

    def add_node(self, node_for_adding: SpatialNode):
        """Adds a SpatialNode to the SpatialGraph

        Args:
            node_for_adding (SpatialNode): a SpatialNode to be added to the graph.

        Raises:
            TypeError: if `node_for_adding` is not a SpatialNode object.
        """
        if not isinstance(node_for_adding, SpatialNode):
            raise TypeError(
                "'node_for_adding' should be a SpatialNode. "
                f"Received {type(node_for_adding)} instead."
            )
        MultiGraph.add_node(
            self, node_for_adding=node_for_adding["name"], **node_for_adding
        )

    def add_edge(self, edge_to_add: SpatialEdge):
        """Adds a SpatialEdge to the SpatialGraph

        Args:
            edge_to_add (SpatialEdge): a SpatialEdge to be added to the graph.

        Raises:
            TypeError: if `edge_to_add` is not a SpatialEdge
            ValueError: if `edge_to_add['start']` is not in the graph.
            ValueError: if `edge_to_add['stop']` is not in the graph.
            TypeError: if `edge_to_add['geometry']` is not a shapely.geometry.LineString object or None.
        """
        if not isinstance(edge_to_add, SpatialEdge):
            raise TypeError(
                "'edge_for_adding' should be a SpatialNode. "
                f"Received {type(edge_to_add)} instead."
            )
        elif edge_to_add["start"] not in self.nodes:
            raise ValueError(
                f"`edge_to_add['start']` '{edge_to_add['start']}' is not a node of this graph."
            )
        elif edge_to_add["stop"] not in self.nodes:
            raise ValueError(
                f"`edge_to_add['stop']` '{edge_to_add['stop']}' is not a node of this graph."
            )
        elif edge_to_add["geometry"] is None:
            edge_to_add["geometry"] = LineString(
                [
                    self.nodes[edge_to_add["start"]]["geometry"],
                    self.nodes[edge_to_add["stop"]]["geometry"],
                ]
            )
        elif not isinstance(edge_to_add["geometry"], LineString):
            raise TypeError(
                "`edge_to_add['geometry']` should be a shapely.geometry.LineString or None. "
                f"Received `{type(edge_to_add['geometry'])}`."
            )
        if "length" not in edge_to_add:
            edge_to_add["length"] = edge_to_add["geometry"].length
        MultiGraph.add_edge(
            self, edge_to_add["start"], edge_to_add["stop"], key=None, **edge_to_add
        )

    def get_points(self):
        """Returns all node positions as a shapely.geometry.MultiPoint object

        Returns:
            shapely.geometry.MultiPoint: a MultiPoint object containing all the node positions
        """
        return MultiPoint([n[1]["geometry"] for n in self.nodes(data=True)])

    def get_segments(self, include: list = None, exclude: list = None):
        """Returns all edge shapes as a shapely.geometry.MultiLineString object

        Args:
            include (list, optional): list of edges to include.
                Defaults to None.
            exclude (list, optional): list of edges to exclude.
                Defaults to None.

        Returns:
            shapely.geometry.MultiLineString: a MultiPoint object containing all the edge shapes
        """
        if include:
            edges = self.edges(nbunch=include, data=True)
        else:
            edges = self.edges(data=True, keys=True)
        if exclude:
            edges = [e for e in edges if (e[0], e[1], e[2]) not in exclude]

        result = MultiLineString([e[3]["geometry"] for e in edges])
        return result

    def draw_nodes(
        self,
        node_color: str = "#EDC339",
        node_size: int = 100,
        include_names: bool = False,
        ax=None,
        figsize: tuple = (5, 5),
    ):
        """Returns a figure with the nodes of the SpatialGraph

        Args:
            node_color (str, optional): color used to represent nodes.
                Defaults to "#EDC339".
            node_size (int, optional): size used to represent nodes.
                Defaults to 100.
            include_names (bool, optional): if True, annotates the names of the nodes.
                Defaults to False.
            ax: Matplotlib Axes object.
                Defaults to None.
            figsize (tuple, optional): size of the figure if ax is None.
                Defaults to (5, 5).

        Returns:
            Matplotlib Axes object.
        """
        if not ax:
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        xs, ys = [], []

        node_properties = {n[0]: n[1] for n in self.nodes(data=True)}

        for n in node_properties:
            xs.append(node_properties[n]["geometry"].x)
            ys.append(node_properties[n]["geometry"].y)

        ax.scatter(xs, ys, color=node_color, s=node_size)

        if include_names:
            for n in node_properties:
                node = node_properties[n]
                ax.annotate(
                    text=node["name"],
                    xy=node["geometry"].coords[0],
                    ha="center",
                    va="center",
                )
        return ax

    def draw_edges(
        self,
        edge_color: str = "#01577D",
        ax=None,
        figsize: tuple = (5, 5),
    ):
        """Returns a figure with the edges of the SpatialGraph

        Args:
            edge_color (str, optional): color used to represent the edges.
                Defaults to "#01577D".
            ax: Matplotlib Axes object.
                Defaults to None.
            figsize (tuple, optional): size of the figure if ax is None.
                Defaults to (5, 5).

        Returns:
            Matplotlib Axes object.
        """
        if not ax:
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        for e in self.edges(data=True, keys=True):
            coordinates = np.asarray(e[3]["geometry"].coords)
            ax.plot(coordinates[:, 0], coordinates[:, 1], color=edge_color, zorder=-1)
        return ax

    def draw(
        self,
        include_names: bool = False,
        include_axis: bool = False,
        ax=None,
        figsize: tuple = (5, 5),
        aspect_ratio: float = None,
    ):
        """Returns a figure with the complete SpatialGraph

        Args:
            include_names (bool, optional): if True, annotates the names of the nodes.
                Defaults to False.
            include_axis (bool, optional): if True, draws the axis.
                Defaults to False.
            ax: Matplotlib Axes object.
                Defaults to None.
            figsize (tuple, optional): size of the figure if ax is None.
                Defaults to (5, 5).
            aspect_ratio (float, optional): aspect ratio between x and y.
                Defaults to None.

        Returns:
            Matplotlib Axes object.
        """

        if not ax:
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        self.draw_edges(ax=ax)
        self.draw_nodes(ax=ax, include_names=include_names)
        if not include_axis:
            ax.axis("off")
        if aspect_ratio is not None:
            ax.set_aspect(aspect_ratio)
        return ax

    def add_edges_from(self, edges_to_add: list):
        """Adds multiple SpatialEdge objects to the SpatialGraph

        Args:
            edges_to_add (list): a list of SpatialEdge objects to add to the graph.
        """
        for e in edges_to_add:
            self.add_edge(e)

    def add_nodes_from(self, nodes_to_add: list):
        """Adds multiple SpatialNode to the SpatialGraph

        Args:
            nodes_to_add (list): a list of SpatialNode objects to add to the graph.
        """
        for n in nodes_to_add:
            self.add_node(n)

    def remove_edge(self, edge_to_remove, key: int = None):
        """Removes an edge from the graph

        Args:
            edge_to_remove (SpatialEdge): the reference of the edge to remove.
                This argument should be a SpatialEdge but you can also pass a tuple
                containing the start and end node names.
            key (int, optional): index of the edge to remove.
                Defaults to None.
        """
        if isinstance(edge_to_remove, SpatialEdge):
            u, v = edge_to_remove["start"], edge_to_remove["stop"]
            MultiGraph.remove_edge(self, u=u, v=v, key=key)
        else:
            u, v = edge_to_remove
            MultiGraph.remove_edge(self, u=u, v=v, key=key)

    def remove_node(self, n):
        """Removes a node from the graph

        Args:
            n (SpatialNode): the reference of the node to remove.
                This argument should be a SpatialNode but you can also pass a Hashable
                object representing the name of the node.
        """
        if isinstance(n, SpatialNode):
            MultiGraph.remove_node(self, n=n["name"])
        elif isinstance(n, Hashable):
            MultiGraph.remove_node(self, n=n)
        else:
            raise TypeError(
                f"'n' should be a 'SpatialNode' or a hashable object, not {type(n)}"
            )

    def remove_edges_from(self, edges_to_remove: list):
        """Removes multiple edges from the graph

        Args:
            edges_to_remove (list): list of edges to remove (see remove_edge)
        """
        for e in edges_to_remove:
            self.remove_edge(edge_to_remove=e)

    def _get_nodes(self):
        return [SpatialNode(**n[1]) for n in self.nodes(data=True)]

    def _get_edges(self):
        return [SpatialEdge(**e[3]) for e in self.edges(data=True, keys=True)]

    def remove_nodes_from(self, nodes_to_remove: list):
        """Removes multiple nodes from the graph

        Args:
            nodes_to_remove (list): list of nodes to remove (see remove_node)
        """
        for n in nodes_to_remove:
            self.remove_node(node_to_remove=n)

    def route_distance(self, node_i_name: str, node_j_name: str):
        """Computes the route distance between two nodes.
        The route distance is the distance computed by using the shortest path.

        Args:
            node_i_name (str): name of the first node
            node_j_name (str): name of the second node

        Returns:
            float: route distance between `node_i_name` and `node_j_name`
        """
        try:
            return nx.shortest_path_length(
                self, source=node_i_name, target=node_j_name, weight="length"
            )
        except nx.NetworkXNoPath:
            return np.NaN

    def metric_distance(self, node_i_name: str, node_j_name: str):
        """Computes the metric distance between two nodes.
        The metric distance is the distance 'as crow flies' between nodes.

        Args:
            node_i_name (str): name of the first node
            node_j_name (str): name of the second node

        Returns:
            float: metric distance between `node_i_name` and `node_j_name`
        """
        node_properties = {n[0]: n[1] for n in self.nodes(data=True)}
        node_i = node_properties[node_i_name]
        node_j = node_properties[node_j_name]

        return node_i["geometry"].distance(node_j["geometry"])

    def detour_index(self, node_i_name: str, node_j_name: str):
        """Computes the detour index between two nodes.
        The detour index is the ratio of the route distance by the metric distance.
        It measures how much detour using the graph implies.

        Args:
            node_i_name (str): name of the first node
            node_j_name (str): name of the second node

        Returns:
            float: detour index between `node_i_name` and `node_j_name`
        """
        return self.route_distance(node_i_name, node_j_name) / self.metric_distance(
            node_i_name, node_j_name
        )
