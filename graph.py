from collections import namedtuple
from random import shuffle

from dfs import dfs_paths, dfs_incremental_routes, dfs_mincut_search
import plantuml

Flow = namedtuple('Flow', ['value', 'max_value'])


def walk(path):
    p0 = path[0]
    for i in range(1, len(path)):
        yield p0, path[i]
        p0 = path[i]


class Graph:
    def __init__(self, graph_dict, start_vertex, target_vertex):
        """
        :param graph_dict: graph_dict[from_vertex][to_vertex] = max_flow
        """

        self.start_vertex = start_vertex
        self.target_vertex = target_vertex

        self.flows = {}
        for from_vertex in graph_dict.keys():
            self.flows[from_vertex] = {}
            for to_vertex in graph_dict.get(from_vertex).keys():
                max_flow = graph_dict[from_vertex][to_vertex]
                self.flows[from_vertex][to_vertex] = Flow(0, max_flow)

        self.paths = dfs_paths(self.flows, self.start_vertex, self.target_vertex)
        shuffle(self.paths)

    def __getitem__(self, item):
        return self.flows.__getitem__(item)

    def get_flow(self, from_vertex, to_vertex):
        return self.flows[from_vertex][to_vertex]

    def increment_flow(self, from_vertex, to_vertex, by_value):
        f = self.get_flow(from_vertex, to_vertex)
        self.flows[from_vertex][to_vertex] = Flow(f.value + by_value, f.max_value)

    def is_saturated_flow(self, from_vertex, to_vertex):
        f = self.flows[from_vertex][to_vertex]
        assert f.value <= f.max_value
        return f.value == f.max_value

    def get_reversed(self):
        reversed_graph = {key: {} for key in self.flows.keys()}
        for i in self.flows.keys():
            for j in self.flows[i].keys():
                reversed_graph[j][i] = self.flows[i][j]
        return reversed_graph

    def get_incremental_routes(self):
        return dfs_incremental_routes(self)

    def get_mincut(self):
        mincut = dfs_mincut_search(self)
        flow = 0
        X1 = {v for v, x in mincut}
        X2 = set(self.flows.keys()) - X1
        for v in X1:
            for j in self.flows[v].keys():
                if j in X2:
                    flow += self.flows[v][j].value
        return mincut, flow

    def current_state_image(self, marked=None):
        return plantuml.get_url(plantuml.build_graph(self.flows, marked))
