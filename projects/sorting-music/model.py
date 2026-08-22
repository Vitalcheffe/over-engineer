"""Sorting Algorithms as Music — Sonification"""
import numpy as np, json
def bubble_sort(arr):
    comparisons = []
    a = arr.copy()
    n = len(a)
    for i in range(n):
        for j in range(n-i-1):
            comparisons.append(('compare', j, j+1, a[j], a[j+1]))
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                comparisons.append(('swap', j, j+1, a[j], a[j+1]))
    return comparisons
def quick_sort_trace(arr):
    comparisons = []
    def qs(a, lo, hi):
        if lo >= hi: return
        pivot = a[hi]
        i = lo - 1
        for j in range(lo, hi):
            comparisons.append(('compare', j, hi, a[j], pivot))
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                comparisons.append(('swap', i, j, a[i], a[j]))
        a[i+1], a[hi] = a[hi], a[i+1]
        comparisons.append(('swap', i+1, hi, a[i+1], a[hi]))
        qs(a, lo, i)
        qs(a, i+2, hi)
    qs(arr.copy(), 0, len(arr)-1)
    return comparisons
def merge_sort_trace(arr):
    comparisons = []
    def ms(a, lo, hi):
        if lo >= hi: return
        mid = (lo+hi)//2
        ms(a, lo, mid)
        ms(a, mid+1, hi)
        merged = []
        i, j = lo, mid+1
        while i <= mid and j <= hi:
            comparisons.append(('compare', i, j, a[i], a[j]))
            if a[i] <= a[j]:
                merged.append(a[i]); i += 1
            else:
                merged.append(a[j]); j += 1
        while i <= mid: merged.append(a[i]); i += 1
        while j <= hi: merged.append(a[j]); j += 1
        for k, v in enumerate(merged):
            a[lo+k] = v
    ms(arr.copy(), 0, len(arr)-1)
    return comparisons
def analyze_entropy(comparisons):
    """Compute Shannon entropy of value distribution."""
    values = [c[3] for c in comparisons if c[0] == 'compare']
    if not values: return 0
    hist, _ = np.histogram(values, bins=32)
    hist = hist / hist.sum()
    return float(-np.sum(hist * np.log2(hist + 1e-10)))
if __name__ == '__main__':
    arr = list(range(32, 0, -1))  # reverse sorted
    bubble = bubble_sort(arr)
    quick = quick_sort_trace(arr)
    merge = merge_sort_trace(arr)
    results = {
        'bubble_sort': {'comparisons': len(bubble), 'entropy': analyze_entropy(bubble)},
        'quick_sort': {'comparisons': len(quick), 'entropy': analyze_entropy(quick)},
        'merge_sort': {'comparisons': len(merge), 'entropy': analyze_entropy(merge)},
    }
    print("Sorting Algorithms as Music:")
    for name, r in results.items():
        print(f"  {name}: {r['comparisons']} comparisons, entropy={r['entropy']:.2f} bits")
    with open('data/results.json', 'w') as f: json.dump(results, f, indent=2)
