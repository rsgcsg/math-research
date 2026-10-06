#!/usr/bin/env python3
"""Exact replay of T172: identity-sensitive robustness of the T165 separator.

This checker uses only integer/rational arithmetic.  It does not enumerate
colorings: T165 already certifies the pointwise separator on the boundary face.
Here we verify the optimal classwise gauge reduction and the resulting sharp
L-infinity consequence of that single separator plus the three class-total
equalities.
"""
from fractions import Fraction as F
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "certificates/q_joint_boundary_gap.json"
CERT = ROOT / "certificates/identity_sensitive_robustness.json"


def require(cond, msg):
    if not cond:
        raise ValueError(msg)


def median_int(values):
    s = sorted(values)
    require(len(s) % 2 == 1, "odd class size expected")
    return s[len(s)//2]


def main():
    src = json.loads(SOURCE.read_text())
    cert = json.loads(CERT.read_text())
    require(src["schema"] == "q-joint-boundary-gap-v1", "source schema")
    require(cert["schema"] == "identity-sensitive-robustness-v1", "certificate schema")
    terms = src["boundary"]["terms"]
    rhs = src["boundary"]["rhs"]
    by = {k: [t["coefficient"] for t in terms if t["type"] == k]
          for k in ("P", "Q", "R")}
    require({k: len(v) for k,v in by.items()} == {"P":47,"Q":11,"R":31},
            "event class sizes")
    sums = {k: sum(v) for k,v in by.items()}
    require(sums == cert["coefficient_sums"] == {"P":-2267,"Q":500,"R":-501},
            "coefficient sums")

    target = {k: F(*cert["target_means"][k]) for k in ("P","Q","R")}
    target_value = sum(F(sums[k]) * target[k] for k in ("P","Q","R"))
    require(target_value == F(*cert["target_separator_value"]) == F(169,27),
            "target separator value")
    gap = target_value - rhs
    require(gap == F(*cert["separator_gap"]) == F(115,27), "separator gap")

    medians = {k: median_int(v) for k,v in by.items()}
    require(medians == cert["class_gauge_medians"] == {"P":-21,"Q":46,"R":0},
            "class medians")
    centered = {k: [a-medians[k] for a in by[k]] for k in by}
    l1s = {k: sum(abs(x) for x in centered[k]) for k in centered}
    require(l1s == {k:cert["class_centered_l1"][k] for k in ("P","Q","R")},
            "class L1 norms")
    total_l1 = sum(l1s.values())
    require(total_l1 == cert["class_centered_l1"]["total"] == 4469, "total L1")

    # Median minimizes sum |a-c| over a real classwise gauge constant c.
    # For odd cardinalities the listed median is the unique minimizing interval point.
    for k, vals in by.items():
        m = medians[k]
        require(all(sum(abs(a-m) for a in vals) <= sum(abs(a-c) for a in vals)
                    for c in range(min(vals)-2, max(vals)+3)),
                "integer median minimum "+k)

    eps = gap / total_l1
    require(eps == F(*cert["minimum_forced_linf_deviation"]) == F(115,120663),
            "forced Linf deviation")

    # Sharpness for the relaxation using only class totals and this separator.
    # d = target - x.  On nonzero centered coefficients choose d=eps*sign(beta).
    # For R there is one excess negative sign; one zero-beta coordinate gets +eps.
    sign_counts = {}
    deltas = {}
    for k, vals in centered.items():
        pos = sum(x>0 for x in vals); neg = sum(x<0 for x in vals); zero = sum(x==0 for x in vals)
        sign_counts[k] = [pos,neg,zero]
        d = [eps if x>0 else -eps if x<0 else F(0) for x in vals]
        if k == "R":
            require(sum(d) == -eps and zero >= 1, "R imbalance before zero repair")
            d[vals.index(0)] = eps
        require(sum(d) == 0, "class-total preserving sharp displacement "+k)
        deltas[k] = d
    require(sign_counts == {
        "P":cert["sharp_single_separator_relaxation"]["P_sign_counts"],
        "Q":cert["sharp_single_separator_relaxation"]["Q_sign_counts"],
        "R":cert["sharp_single_separator_relaxation"]["R_sign_counts"]},
        "sign counts")
    achieved = sum(F(b)*d for k in centered for b,d in zip(centered[k],deltas[k]))
    require(achieved == gap, "sharp displacement saturates separator")
    require(max(abs(d) for ds in deltas.values() for d in ds) == eps, "sharp Linf norm")

    # The synthetic marginal vector stays in [0,1], so box constraints do not improve
    # the single-separator relaxation at this scale.
    for k in deltas:
        for d in deltas[k]:
            x = target[k] - d
            require(0 <= x <= 1, "sharp synthetic marginal in probability box")

    print(json.dumps({
        "status":"PASS",
        "research_id":"T172",
        "gap":[gap.numerator,gap.denominator],
        "optimal_class_gauge_l1":total_l1,
        "forced_linf":[eps.numerator,eps.denominator],
        "sign_counts":sign_counts,
        "scope":cert["scope"]
    }, sort_keys=True))


if __name__ == "__main__":
    main()