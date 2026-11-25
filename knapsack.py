"""knapsack.py - 0/1 Knapsack by Dynamic Programming.

Decides which parcels go on ONE delivery trip.
  weight   -> parcel weight
  value    -> parcel priority (higher = more worth loading)
  capacity -> vehicle capacity
Time O(n*W), Space O(n*W).
"""


def knapsack(parcels, capacity):
    n = len(parcels)
    # dp[i][w] = best total priority using the first i parcels with weight limit w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wt, val = parcels[i - 1].weight, parcels[i - 1].priority
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]                       # skip parcel i
            if wt <= w:                                   # or take parcel i
                dp[i][w] = max(dp[i][w], dp[i - 1][w - wt] + val)

    # walk the table backwards to find WHICH parcels were chosen
    chosen, w = [], capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(parcels[i - 1])
            w -= parcels[i - 1].weight
    chosen.reverse()
    return chosen, dp[n][capacity], dp
