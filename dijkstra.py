"""dijkstra.py - Single-source shortest paths using a min-heap. O((V+E) log V)."""
import heapq


def dijkstra(graph, source):
    dist = {node: float("inf") for node in graph.adj}
    prev = {node: None for node in graph.adj}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                      # stale heap entry
        for v, w in graph.adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, prev


def get_path(prev, target):
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    return path[::-1]
