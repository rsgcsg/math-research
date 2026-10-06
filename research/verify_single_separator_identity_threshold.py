#!/usr/bin/env python3
"""Exact replay of T173: sparsity ceiling for the single T165 separator.

We ask how many individual event marginals must be fixed to the C030 targets
before the relaxation consisting only of the three P/Q/R class-total equalities,
probability boxes, and the T165 boundary separator becomes infeasible.

The optimization is solved exactly by an order-statistic dynamic program using
fractions; no LP solver or floating point is used.
"""
from fractions import Fraction as F
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "certificates/q_joint_boundary_gap.json"
CERT = ROOT / "certificates/single_separator_identity_threshold.json"

def require(cond, msg):
    if not cond:
        raise ValueError(msg)

def floor_fraction(x):
    return x.numerator // x.denominator

def class_best_escape(items, target, free_count, want_choice=False):
    items = sorted(items, key=lambda z: (z[0], z[1]))
    n = len(items)
    m = free_count
    require(0 <= m <= n, "free count range")
    if m == 0:
        return (F(0), []) if want_choice else F(0)
    mass = F(m) * target
    q = floor_fraction(mass)
    frac = mass - q
    weights = []
    for j in range(1, m+1):
        if j <= q:
            weights.append(target - 1)
        elif j == q+1 and frac:
            weights.append(target - frac)
        else:
            weights.append(target)
    dp = [(F(0), [])] + [None] * m
    for idx, (a, pair) in enumerate(items):
        for j in range(min(m, idx+1), 0, -1):
            prev = dp[j-1]
            if prev is None:
                continue
            cand = (prev[0] + weights[j-1] * a, prev[1] + [idx])
            if dp[j] is None or cand[0] < dp[j][0]:
                dp[j] = cand
    require(dp[m] is not None, "DP completion")
    value = dp[m][0]
    require(value >= 0, "escape nonnegative")
    if want_choice:
        chosen = [items[i] for i in dp[m][1]]
        return value, chosen
    return value

def eval_free_escape(coeffs, target):
    vals = sorted(coeffs)
    m = len(vals)
    if not m:
        return F(0)
    mass = F(m) * target
    q = floor_fraction(mass)
    frac = mass-q
    minimum = sum(vals[:q], 0)
    if frac:
        minimum += frac * vals[q]
    return target * sum(vals) - minimum

def main():
    src = json.loads(SOURCE.read_text())
    cert = json.loads(CERT.read_text())
    require(src["schema"] == "q-joint-boundary-gap-v1", "source schema")
    require(cert["schema"] == "single-separator-identity-threshold-v1", "cert schema")
    terms = src["boundary"]["terms"]
    target = {k:F(*cert["target_means"][k]) for k in ("P","Q","R")}
    items = {}
    for k in ("P","Q","R"):
        items[k] = [(t["coefficient"], tuple(t["pair"])) for t in terms if t["type"] == k]
    require({k:len(items[k]) for k in items} == {"P":47,"Q":11,"R":31}, "class counts")
    require(sum(len(v) for v in items.values()) == cert["event_counts"]["total"] == 89,
            "total event count")

    class_escape = {
        k:[class_best_escape(items[k], target[k], m) for m in range(len(items[k])+1)]
        for k in items
    }
    gap = F(*cert["target_gap"])
    global_best = {}
    for mp in range(48):
        for mq in range(12):
            for mr in range(32):
                fixed = 89-(mp+mq+mr)
                val = class_escape["P"][mp] + class_escape["Q"][mq] + class_escape["R"][mr]
                old = global_best.get(fixed)
                if old is None or val < old[0]:
                    global_best[fixed] = (val,(mp,mq,mr))
    require(global_best[70] == (F(*cert["best_escape_at_70_fixed"]), (11,2,6)),
            "exact 70-fixed boundary")
    require(global_best[71] == (F(*cert["best_escape_at_71_fixed"]), (10,2,6)),
            "exact 71-fixed boundary")
    require(global_best[70][0] == gap and global_best[71][0] < gap,
            "threshold crosses strict separator gap")
    require(all(global_best[k][0] >= gap for k in range(0,71)),
            "no <=70 fixed identities force the single separator")
    require(cert["fixed_identity_threshold"] == 71, "reported threshold")

    prescribed = cert["one_optimal_71_fixed_complement"]
    for k in ("P","Q","R"):
        available = {(tuple(pair), coeff) for coeff,pair in items[k]}
        rows = [(tuple(pair), coeff) for pair,coeff in prescribed[k]]
        require(len(rows) == len(set(rows)) and all(row in available for row in rows),
                "prescribed free rows are actual "+k+" terms")
    require({k:len(prescribed[k]) for k in prescribed} == {"P":10,"Q":2,"R":6},
            "prescribed free counts")
    prescribed_escape = sum(
        eval_free_escape([coeff for pair,coeff in prescribed[k]], target[k])
        for k in ("P","Q","R")
    )
    require(prescribed_escape == F(32,9) == global_best[71][0],
            "explicit complement attains 71-fixed optimum")

    esc70 = F(0)
    for k,m in zip(("P","Q","R"),(11,2,6)):
        val, chosen = class_best_escape(items[k], target[k], m, True)
        require(len(chosen) == m, "70-fixed witness size")
        esc70 += val
    require(esc70 == gap, "70-fixed equality witness")

    print(json.dumps({
        "status":"PASS",
        "research_id":"T173",
        "threshold":71,
        "fixed70":{"best_escape":[gap.numerator,gap.denominator],"free_counts":[11,2,6]},
        "fixed71":{"best_escape":[global_best[71][0].numerator,global_best[71][0].denominator],
                   "free_counts":[10,2,6]},
        "explicit_71_free_complement_verified":True,
        "scope":cert["scope"]
    }, sort_keys=True))

if __name__ == "__main__":
    main()
