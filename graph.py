"""graph.py - Undirected weighted graph stored as an adjacency list."""


class Graph:
    def __init__(self):
        self.adj = {}  # node -> list of (neighbour, weight)

    def add_edge(self, u, v, w):
        self.adj.setdefault(u, []).append((v, w))
        self.adj.setdefault(v, []).append((u, w))

    @classmethod
    def from_edges(cls, edges):
        g = cls()
        for u, v, w in edges:
            g.add_edge(u, v, w)
        return g

    def nodes(self):
        return list(self.adj)
