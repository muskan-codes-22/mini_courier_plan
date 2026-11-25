"""performance.py - Timing helpers, CSV export and runtime chart."""
import csv
import time


def timed(fn, *args, repeat=1):
    """Run fn(*args) and return (result, average seconds)."""
    start = time.perf_counter()
    for _ in range(repeat):
        result = fn(*args)
    return result, (time.perf_counter() - start) / repeat


def save_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "parcels", "step", "runtime_ms"])
        w.writerows(rows)


def save_chart(rows, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping chart (pip install matplotlib)")
        return
    datasets = list(dict.fromkeys(r[0] for r in rows))
    steps = list(dict.fromkeys(r[2] for r in rows))
    width = 0.8 / len(datasets)
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, d in enumerate(datasets):
        vals = [next(r[3] for r in rows if r[0] == d and r[2] == s) for s in steps]
        ax.bar([x + i * width for x in range(len(steps))], vals, width, label=d)
    ax.set_xticks([x + width * (len(datasets) - 1) / 2 for x in range(len(steps))])
    ax.set_xticklabels(steps, rotation=20, ha="right")
    ax.set_ylabel("Runtime (ms)")
    ax.set_yscale("log")
    ax.set_title("Mini-Courier Planner - runtime per step")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Chart saved to {path}")
