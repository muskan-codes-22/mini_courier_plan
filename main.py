"""main.py - Mini-Courier Planner: runs the whole pipeline on small & large datasets.

Pipeline:  load -> sort parcels (Merge Sort) -> pick trip load (0/1 Knapsack DP)
           -> build graph -> shortest paths (Dijkstra) -> route (Nearest-Neighbour TSP)
"""
import os
from parcels import load_dataset, generate_dataset
from graph import Graph
from sorting import merge_sort, quick_sort
from knapsack import knapsack
from tsp import nearest_neighbor_route
from performance import timed, save_csv, save_chart

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
RESULTS = os.path.join(BASE, "results")


def ensure_datasets():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)
    small = os.path.join(DATA, "small_dataset.json")
    large = os.path.join(DATA, "large_dataset.json")
    if not os.path.exists(small):
        generate_dataset(small, n_parcels=10, n_nodes=7, capacity=20, seed=1)
    if not os.path.exists(large):
        generate_dataset(large, n_parcels=1000, n_nodes=200, capacity=300, seed=2)
    return {"small": small, "large": large}


def run(name, path, verbose, rows):
    parcels, edges, depot, capacity = load_dataset(path)
    n = len(parcels)
    print(f"\n{'=' * 60}\nDATASET: {name}  ({n} parcels, vehicle capacity {capacity} kg)\n{'=' * 60}")

    # Phase 2a - prioritise
    sorted_parcels, t_merge = timed(merge_sort, parcels)
    _, t_quick = timed(quick_sort, parcels)
    # Phase 2b - choose the trip load
    (chosen, best_value, dp), t_knap = timed(knapsack, sorted_parcels, capacity)
    # Phase 3a - graph
    graph, t_graph = timed(Graph.from_edges, edges)
    # Phase 3b - route (Dijkstra is called inside the TSP step)
    stops = {p.destination for p in chosen}
    (route, length, full_path), t_route = timed(nearest_neighbor_route, graph, depot, stops)

    if verbose:
        print("\nParcels sorted by deadline, then priority (first 10):")
        for p in sorted_parcels[:10]:
            print(f"  {p.id:<4} deadline={p.deadline}d  priority={p.priority:<2} "
                  f"weight={p.weight:<2}kg -> {p.destination}")
        print(f"\nKnapsack: loaded {len(chosen)} parcels, "
              f"{sum(p.weight for p in chosen)}/{capacity} kg, total priority {best_value}")
        print("  Selected:", ", ".join(p.id for p in chosen))
        print(f"\nDelivery stops: {sorted(stops)}")
        print("Route (stops only):", " -> ".join(route))
        print("Route (roads used):", " -> ".join(full_path))
    else:
        print(f"Knapsack loaded {len(chosen)} parcels (priority {best_value}), "
              f"visiting {len(stops)} stops")
        print(f"Route visits {len(route) - 2} stops, total length = {length}")
    print(f"TOTAL ROUTE LENGTH: {length}")

    ms = lambda t: round(t * 1000, 4)
    for step, t in [("Merge Sort", t_merge), ("Quick Sort", t_quick),
                    ("Knapsack DP", t_knap), ("Build Graph", t_graph),
                    ("Dijkstra + TSP", t_route)]:
        rows.append((name, n, step, ms(t)))
        print(f"  {step:<15}{ms(t):>10} ms")


if __name__ == "__main__":
    files = ensure_datasets()
    rows = []
    run("small", files["small"], verbose=True, rows=rows)
    run("large", files["large"], verbose=False, rows=rows)
    save_csv(rows, os.path.join(RESULTS, "runtime_results.csv"))
    save_chart(rows, os.path.join(RESULTS, "runtime_chart.png"))
    print("\nSaved results/runtime_results.csv")
