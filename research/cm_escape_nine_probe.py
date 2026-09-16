"""Nine-point CM-host escape; a producer, not its own proof checker.

Q(a,b,h): a^2=3, b^2=11, h^2=(1+ab)/8; all three chosen positive.
No SAT.  The entire induced graph is independently four-colorable.
"""

from fractions import Fraction as Q
import json


def f(values=()):
    values = tuple(map(Q, values))
    return values + (Q(0),) * (8 - len(values))


ZERO, ONE = f(), f([1])


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def sub(x, y):
    return tuple(a - b for a, b in zip(x, y))


def mul4(x, y):
    out = [Q(0)] * 4
    for i, xi in enumerate(x):
        for j, yj in enumerate(y):
            out[i ^ j] += xi * yj * (3 if i & j & 1 else 1) * (11 if i & j & 2 else 1)
    return tuple(out)


def mul(x, y):
    low = add(mul4(x[:4], y[:4]), mul4(mul4(x[4:], y[4:]), (Q(1, 8), 0, 0, Q(1, 8))))
    high = add(mul4(x[:4], y[4:]), mul4(x[4:], y[:4]))
    return low + high


def sqdist(p, q):
    dx, dy = sub(p[0], q[0]), sub(p[1], q[1])
    return add(mul(dx, dx), mul(dy, dy))


def construct():
    names = ["s", "t", "x", "y", "p", "u", "v", "w", "z"]
    pts = [
        (f([Q(-1, 2)]), ZERO),
        (f([Q(1, 2)]), ZERO),
        (ZERO, f([0, 0, Q(1, 2)])),
        (ZERO, f([0, Q(1, 2)])),
        (f([0, 0, 0, 0, 1]), f([0, Q(1, 4), Q(1, 4)])),
        (f([Q(-1, 4), 0, 0, Q(-1, 12)]), f([0, Q(1, 12), Q(1, 4)])),
        (f([Q(-1, 4), 0, 0, Q(1, 12)]), f([0, Q(-1, 12), Q(1, 4)])),
        (f([Q(1, 4), 0, 0, Q(-1, 12)]), f([0, Q(-1, 12), Q(1, 4)])),
        (f([Q(1, 4), 0, 0, Q(1, 12)]), f([0, Q(1, 12), Q(1, 4)])),
    ]
    # One Moser spindle: common apex x, outer apices s,t, transverse edge st.
    spindle_edges = [(0, 1), (0, 5), (0, 6), (2, 5), (2, 6), (5, 6),
                     (1, 7), (1, 8), (2, 7), (2, 8), (7, 8)]
    extra = [(0, 3), (1, 3), (2, 4), (3, 4)]
    listed = sorted(spindle_edges + extra)
    actual = [(i, j) for i in range(9) for j in range(i + 1, 9)
              if sqdist(pts[i], pts[j]) == ONE]
    assert len(set(pts)) == 9
    assert actual == listed
    assert sqdist(pts[0], pts[2]) == f([3])
    assert sqdist(pts[1], pts[2]) == f([3])
    assert sqdist(pts[2], pts[3]) == f([Q(7, 2), 0, 0, Q(-1, 2)])
    return names, pts, actual


def color(n, edges, k):
    """Tiny backtracking used only to produce a directly checked positive word."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    colors = [-1] * n
    def visit():
        remaining = [v for v in range(n) if colors[v] < 0]
        if not remaining:
            return tuple(colors)
        v = max(remaining, key=lambda v: (len({colors[u] for u in adj[v] if colors[u] >= 0}), len(adj[v]), -v))
        banned = {colors[u] for u in adj[v] if colors[u] >= 0}
        for c in range(min(k, max(colors) + 2)):
            if c not in banned:
                colors[v] = c
                out = visit()
                if out is not None:
                    return out
        colors[v] = -1
        return None
    return visit()


def main():
    if not __debug__:
        raise SystemExit("Refusing optimized Python: assertions are required.")
    names, pts, edges = construct()
    word = color(9, edges, 4)
    assert word is not None and all(word[u] != word[v] for u, v in edges)
    obj = dict(schema=1, experiment="E091", scope="CM-host exclusion only; no HN improvement",
               basis=["1", "sqrt(3)", "sqrt(11)", "sqrt(33)", "h", "sqrt(3)*h", "sqrt(11)*h", "sqrt(33)*h"],
               h="positive sqrt((1+sqrt(33))/8)", names=names,
               basic_indices=dict(s=0, t=1, x=2, y=3, p=4),
               coordinates=[[[str(c) for c in x], [str(c) for c in y]] for x, y in pts],
               listed_edges=edges, actual_edges=edges,
               moser_rod=dict(anchor=2, target=0, c=1, u=5, v=6, w=7, z=8),
               proper_four_coloring=word, forced_pair=[2, 3],
               forced_squared_distance="(7-sqrt(33))/2")
    print(json.dumps(obj, separators=(",", ":")))


if __name__ == "__main__":
    main()
