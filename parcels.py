"""parcels.py - Parcel data model, dataset loading and dataset generation."""
import json
import random
from dataclasses import dataclass


@dataclass
class Parcel:
    id: str
    weight: int        # kg, used by knapsack as the item "cost"
    priority: int      # 1 (low) .. 10 (urgent), used by knapsack as the item "value"
    deadline: int      # days until it must be delivered (smaller = more urgent)
    destination: str   # node name in the graph


def load_dataset(path):
    """Read a JSON dataset. Returns (parcels, edges, depot, capacity)."""
    with open(path) as f:
        data = json.load(f)
    parcels = [Parcel(**p) for p in data["parcels"]]
    return parcels, data["edges"], data["depot"], data["capacity"]


def generate_dataset(path, n_parcels, n_nodes, capacity, seed=42):
    """Create a random (but always connected) dataset and save it as JSON."""
    rnd = random.Random(seed)
    nodes = ["Depot"] + [f"C{i}" for i in range(1, n_nodes)]
    edges = []
    # random spanning tree -> guarantees the graph is connected
    for i in range(1, len(nodes)):
        edges.append([nodes[i], nodes[rnd.randrange(i)], rnd.randint(1, 20)])
    # extra edges make shortest-path routing interesting
    for _ in range(n_nodes * 2):
        a, b = rnd.sample(nodes, 2)
        edges.append([a, b, rnd.randint(1, 20)])
    parcels = [
        {
            "id": f"P{i}",
            "weight": rnd.randint(1, 10),
            "priority": rnd.randint(1, 10),
            "deadline": rnd.randint(1, 7),
            "destination": rnd.choice(nodes[1:]),
        }
        for i in range(1, n_parcels + 1)
    ]
    data = {"depot": "Depot", "capacity": capacity, "edges": edges, "parcels": parcels}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
