"""Bounded unrestricted nonlinear positive-only search on H29.

Failure to reach zero monochromatic edges has no mathematical negative scope.
The fixed default seeds and step budget replay the 2026-09-16 diagnostic.
"""
from random import Random
import argparse
import json


def run(seed, steps):
    p, k = 29, 6
    points = [(a, b) for a in range(p) for b in range(p)]
    directions = [(a, b) for a, b in points if (a*a+3*b*b) % p == 1]
    adjacency = [[((a+x) % p)*p+(b+y) % p for x, y in directions]
                 for a, b in points]
    rng = Random(seed)
    colors = [rng.randrange(k) for _ in points]
    count = [[0]*k for _ in points]
    for v, neighbors in enumerate(adjacency):
        for w in neighbors:
            count[v][colors[w]] += 1
    total = sum(count[v][colors[v]] for v in range(p*p))//2
    best = total
    taboo = [[0]*k for _ in points]
    step = 0
    for step in range(1, steps+1):
        delta_best, choices = 100, []
        for v in range(p*p):
            old = colors[v]
            old_count = count[v][old]
            if not old_count:
                continue
            for c in range(k):
                if c == old:
                    continue
                delta = count[v][c]-old_count
                if taboo[v][c] > step and total+delta >= best:
                    continue
                if delta < delta_best:
                    delta_best, choices = delta, [(v, c)]
                elif delta == delta_best:
                    choices.append((v, c))
        if not choices:
            continue
        v, c = rng.choice(choices)
        old = colors[v]
        taboo[v][old] = step+int(.6*total)+rng.randrange(1, 11)
        colors[v] = c
        for w in adjacency[v]:
            count[w][old] -= 1
            count[w][c] += 1
        total += delta_best
        best = min(best, total)
        if not total:
            break
    direct_total = sum(colors[v] == colors[w]
                       for v in range(p*p) for w in adjacency[v])//2
    assert total == direct_total
    result = dict(seed=seed, requested_steps=steps, steps=step,
                  best_monochromatic_edges=best,
                  final_monochromatic_edges=total,
                  status='SAT' if total == 0 else 'NO_POSITIVE_FOUND',
                  scope='No negative mathematical inference.')
    if not total:
        result['word'] = colors
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--steps', type=int, default=100000)
    parser.add_argument('--seed', type=int, nargs='*', default=[202609160, 202609161])
    args = parser.parse_args()
    for seed in args.seed:
        print(json.dumps(run(seed, args.steps), indent=2), flush=True)
