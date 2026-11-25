"""tsp.py - Nearest-Neighbour approximation for the Travelling Salesman Problem.

From the current stop, always drive to the closest unvisited stop, then return to
the depot. Distances between stops come from Dijkstra. Time O(k^2) for k stops.
(Exact TSP is O(k!) / O(k^2 * 2^k), so we trade optimality for speed.)
"""
from dijkstra import dijkstra, get_path


def nearest_neighbor_route(graph, depot, stops):
    stops = set(stops) - {depot}
    cache = {}                                   # Dijkstra result per node

    def shortest(src):
        if src not in cache:
            cache[src] = dijkstra(graph, src)
        return cache[src]

    route, total, current = [depot], 0, depot
    full_path = [depot]
    while stops:
        dist, _ = shortest(current)
        nxt = min(sorted(stops), key=lambda s: dist[s])  # closest unvisited stop (sorted -> ties broken the same way every run)
        total += dist[nxt]
        _, prev = shortest(current)
        full_path += get_path(prev, nxt)[1:]     # real roads travelled
        route.append(nxt)
        stops.remove(nxt)
        current = nxt

    dist, prev = shortest(current)               # return to depot
    total += dist[depot]
    full_path += get_path(prev, depot)[1:]
    route.append(depot)
    return route, total, full_path