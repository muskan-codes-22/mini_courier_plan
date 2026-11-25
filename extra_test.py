"""extra_tests.py - Correctness checks and evidence for the report.

Run from inside the mini_courier_plan folder:   python extra_tests.py
Prints: DP table, brute-force check of knapsack, greedy counter-example,
Dijkstra distance table, Nearest-Neighbour vs optimal tour, sorting checks,
edge cases and averaged runtimes.
"""
import os
import itertools
from parcels import load_dataset, Parcel
from graph import Graph
from sorting import merge_sort, quick_sort, _key
from knapsack import knapsack
from dijkstra import dijkstra, get_path
from tsp import nearest_neighbor_route
from performance import timed

BASE = os.path.dirname(os.path.abspath(__file__))
SMALL = os.path.join(BASE, "data", "small_dataset.json")
LARGE = os.path.join(BASE, "data", "large_dataset.json")


def check(name, ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def header(t):
    print(f"\n{'=' * 64}\n{t}\n{'=' * 64}")


parcels, edges, depot, capacity = load_dataset(SMALL)
graph = Graph.from_edges(edges)
sp = merge_sort(parcels)

# ---------------------------------------------------------------- 1
header("TEST 1: Knapsack DP table (small dataset, parcels in sorted order)")
chosen, best, dp = knapsack(sp, capacity)
print("capacity w:  " + "".join(f"{w:>3}" for w in range(capacity + 1)))
print("i=0 (none):  " + "".join(f"{v:>3}" for v in dp[0]))
for i, p in enumerate(sp, 1):
    print(f"i={i:<2} {p.id:<4}   " + "".join(f"{v:>3}" for v in dp[i]))
print(f"\nBest value dp[n][W] = {best}; backtracking selects: "
      f"{', '.join(p.id for p in chosen)} "
      f"(weight {sum(p.weight for p in chosen)}/{capacity})")

# ---------------------------------------------------------------- 2
header("TEST 2: Knapsack vs brute force (all 2^n subsets)")
bf_best = 0
for r in range(len(sp) + 1):
    for combo in itertools.combinations(sp, r):
        if sum(p.weight for p in combo) <= capacity:
            bf_best = max(bf_best, sum(p.priority for p in combo))
print(f"  DP value = {best}, brute-force value = {bf_best}")
check("DP value equals brute-force optimum", best == bf_best)
check("Total weight <= capacity", sum(p.weight for p in chosen) <= capacity)

# ---------------------------------------------------------------- 3
header("TEST 3: Why greedy fails (W=10; A:w6,v7  B:w5,v5  C:w5,v5)")
items = [Parcel("A", 6, 7, 1, "C1"), Parcel("B", 5, 5, 1, "C1"), Parcel("C", 5, 5, 1, "C1")]
greedy_w, greedy_v = 0, 0
for p in sorted(items, key=lambda p: p.priority / p.weight, reverse=True):
    if greedy_w + p.weight <= 10:
        greedy_w += p.weight
        greedy_v += p.priority
dp_sel, dp_val, _ = knapsack(items, 10)
print(f"  Greedy (best ratio first) value = {greedy_v}")
print(f"  DP value = {dp_val}, selected = {[p.id for p in dp_sel]}")
check("DP beats greedy on this input", dp_val > greedy_v)

# ---------------------------------------------------------------- 4
header("TEST 4: Dijkstra shortest distances from the Depot (small graph)")
dist, prev = dijkstra(graph, depot)
for node in sorted(dist):
    print(f"  Depot -> {node:<6} distance = {dist[node]:<3} path = {' -> '.join(get_path(prev, node))}")
check("All nodes reachable", all(d != float('inf') for d in dist.values()))
check("Depot -> C5 = 6 (direct edge 6 beats Depot-C3-C5 = 15)", dist["C5"] == 6)

# ---------------------------------------------------------------- 5
header("TEST 5: Nearest-Neighbour vs optimal tour (all 6 customers as stops)")
stops = {n for n in graph.adj if n != depot}
route, length, full = nearest_neighbor_route(graph, depot, stops)
D = {n: dijkstra(graph, n)[0] for n in graph.adj}
opt = min(
    sum(D[a][b] for a, b in zip((depot,) + perm, perm + (depot,)))
    for perm in itertools.permutations(sorted(stops))
)
print(f"  NN route : {' -> '.join(route)}  length = {length}")
print(f"  Optimal  : length = {opt}  (brute force over {len(list(itertools.permutations(stops)))} tours)")
print(f"  NN / optimal = {length / opt:.2f}")
check("Every stop visited exactly once", sorted(route[1:-1]) == sorted(stops))
check("Route starts and ends at depot", route[0] == depot and route[-1] == depot)
check("NN length >= optimal length", length >= opt)
r2 = nearest_neighbor_route(graph, depot, stops)[0]
check("Route identical on a second run (deterministic)", route == r2)

# ---------------------------------------------------------------- 6
header("TEST 6: Sorting checks")
big, _, _, _ = load_dataset(LARGE)
check("Merge Sort == Python sorted() on 1000 parcels",
      [p.id for p in merge_sort(big)] == [p.id for p in sorted(big, key=_key)])
check("Quick Sort has the same key order as Merge Sort",
      [_key(p) for p in quick_sort(big)] == [_key(p) for p in merge_sort(big)])
ties = [Parcel(f"T{i}", 1, 5, 3, "C1") for i in range(6)]
check("Merge Sort is stable (equal keys keep input order)",
      [p.id for p in merge_sort(ties)] == [p.id for p in ties])

# ---------------------------------------------------------------- 7
header("TEST 7: Edge cases")
sel, val, _ = knapsack([Parcel("H", 50, 9, 1, "C1")], 20)
check("All parcels heavier than capacity -> empty load, value 0", sel == [] and val == 0)
sel, val, _ = knapsack([], 20)
check("No parcels -> empty load", sel == [] and val == 0)
sel, val, _ = knapsack([Parcel("S", 5, 4, 1, "C1")], 5)
check("Single parcel that exactly fits is loaded", [p.id for p in sel] == ["S"] and val == 4)
r, l, _ = nearest_neighbor_route(graph, depot, set())
check("No stops -> route is just Depot -> Depot, length 0", r == [depot, depot] and l == 0)

# ---------------------------------------------------------------- 8
header("TEST 8: Averaged runtimes (mean of 20 runs, ms)")
print(f"  {'Step':<16}{'Small':>10}{'Large':>12}")
rows = {}
for name, path in (("Small", SMALL), ("Large", LARGE)):
    ps, ed, dep, cap = load_dataset(path)
    _, t_m = timed(merge_sort, ps, repeat=20)
    _, t_q = timed(quick_sort, ps, repeat=20)
    srt = merge_sort(ps)
    (ch, _, _), t_k = timed(knapsack, srt, cap, repeat=20)
    _, t_g = timed(Graph.from_edges, ed, repeat=20)
    g = Graph.from_edges(ed)
    st = {p.destination for p in ch}
    _, t_r = timed(nearest_neighbor_route, g, dep, st, repeat=20)
    rows[name] = [t_m, t_q, t_k, t_g, t_r]
for i, step in enumerate(["Merge Sort", "Quick Sort", "Knapsack DP", "Build Graph", "Dijkstra + TSP"]):
    s, l = rows["Small"][i] * 1000, rows["Large"][i] * 1000
    print(f"  {step:<16}{s:>10.4f}{l:>12.4f}   growth x{l / s:,.0f}")