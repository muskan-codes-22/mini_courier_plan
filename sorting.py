"""sorting.py - Sort parcels by urgency: earliest deadline first, then highest priority.

Merge Sort  : O(n log n) in every case, stable.  <- used by the planner
Quick Sort  : O(n log n) average, O(n^2) worst case. <- kept for comparison
"""


def _key(p):
    return (p.deadline, -p.priority)   # smaller tuple = more urgent


def merge_sort(items):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left, right = merge_sort(items[:mid]), merge_sort(items[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if _key(left[i]) <= _key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def quick_sort(items):
    if len(items) <= 1:
        return items
    pivot = _key(items[len(items) // 2])
    less = [x for x in items if _key(x) < pivot]
    equal = [x for x in items if _key(x) == pivot]
    more = [x for x in items if _key(x) > pivot]
    return quick_sort(less) + equal + quick_sort(more)
