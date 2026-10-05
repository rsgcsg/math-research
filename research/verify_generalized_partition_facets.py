#!/usr/bin/env python3
"""T160/E120: exact audit of generalized clique-partition facets on the T157 P/R core.

Standard-library verifier for all GOW/G2COC instances fitting in the certified
seven-point local P/R/unit core. The general T160 theorem is proved separately.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError("Verification requires assertions; run without -O")

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode()

def sha256(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def unique_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key: " + key)
        out[key] = value
    return out

def read_json(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_keys)

PENTAGON = [
    (F(1, 27), F(14, 27)), (F(1, 6), F(0)), (F(1, 3), F(0)),
    (F(1, 3), F(1, 3)), (F(1, 5), F(3, 5)),
]

def validate_source(cert):
    cert0 = dict(cert)
    stored = cert0.pop("certificate_sha256")
    assert stored == sha256(cert0)
    vertices = cert["local_hex"]["vertices"]
    assert vertices == [4641, 877, 887, 3483, 5535, 7479, 7489]
    pair_tags = {}
    for row in cert["local_hex"]["pair_tags"]:
        edge = tuple(sorted(row["pair"]))
        assert len(edge) == 2 and edge not in pair_tags
        assert row["tag"] in ("P", "R", "unit")
        pair_tags[edge] = row["tag"]
    expected = {tuple(sorted(e)) for e in combinations(vertices, 2)}
    assert set(pair_tags) == expected
    assert Counter(pair_tags.values()) == Counter({"P": 12, "R": 3, "unit": 6})
    return stored, vertices, pair_tags

def project(coefficients, pair_tags):
    p = r = unit = 0
    for edge, coefficient in coefficients.items():
        tag = pair_tags[tuple(sorted(edge))]
        if tag == "P":
            p += coefficient
        elif tag == "R":
            r += coefficient
        else:
            unit += coefficient
    return p, r, unit

def projected_slack(p_coeff, r_coeff, rhs):
    maximum = max(p_coeff * p + r_coeff * r for p, r in PENTAGON)
    return F(rhs) - maximum, maximum

def audit_gow(c, vertices, pair_tags):
    assert c >= 3 and c % 2 == 1
    f = c // 2
    rows = Counter()
    groupings = 0
    for labels in product(range(-1, c + 1), repeat=len(vertices)):
        if 0 not in labels or any((i + 1) not in labels for i in range(c)):
            continue
        first_side = next((x for x in labels if x >= 1), None)
        if first_side != 1:
            continue
        groupings += 1
        coeff = {}
        for i, j in combinations(range(len(vertices)), 2):
            a, b = labels[i], labels[j]
            value = 0
            if a == -1 or b == -1:
                pass
            elif a == 0 and b == 0:
                value = -f
            elif (a == 0) != (b == 0):
                value = 1
            elif a == b:
                value = -1
            else:
                sa, sb = a - 1, b - 1
                if (sa - sb) % c in (1, c - 1):
                    value = -1
            if value:
                coeff[(vertices[i], vertices[j])] = value
        p_coeff, r_coeff, _ = project(coeff, pair_tags)
        rhs = labels.count(0) * f
        rows[(p_coeff, r_coeff, rhs)] += 1
    slacks = {row: projected_slack(row[0], row[1], row[2])[0] for row in rows}
    minimum = min(slacks.values())
    tight = [list(row) for row in sorted(rows) if slacks[row] == 0]
    return {
        "groupings": groupings,
        "unique_projected_rows": len(rows),
        "minimum_slack_on_T158_pentagon": str(minimum),
        "tight_projected_rows_P_R_rhs": tight,
    }

def audit_g2coc(c, total_size, vertices, pair_tags):
    assert c >= 5 and c <= total_size <= len(vertices) and total_size % 2 == 1
    full_rows = Counter()
    projected_rows = Counter()
    groupings = 0
    for subset in combinations(range(len(vertices)), total_size):
        for labels in product(range(c), repeat=total_size):
            if labels[0] != 0 or len(set(labels)) != c:
                continue
            groupings += 1
            assignment = {subset[i]: labels[i] for i in range(total_size)}
            coeff = {}
            for i, j in combinations(subset, 2):
                a, b = assignment[i], assignment[j]
                value = 0
                if a == b:
                    value = -1
                else:
                    distance = (a - b) % c
                    if distance in (1, c - 1):
                        value = 1
                    elif distance in (2, c - 2):
                        value = -1
                if value:
                    coeff[(vertices[i], vertices[j])] = value
            p_coeff, r_coeff, unit_coeff = project(coeff, pair_tags)
            rhs = total_size // 2
            full_rows[(p_coeff, r_coeff, unit_coeff, rhs)] += 1
            projected_rows[(p_coeff, r_coeff, rhs)] += 1
    scored = []
    for p_coeff, r_coeff, unit_coeff, rhs in full_rows:
        slack, maximum = projected_slack(p_coeff, r_coeff, rhs)
        scored.append((slack, p_coeff, r_coeff, unit_coeff, rhs, maximum))
    scored.sort()
    best = scored[0]
    return {
        "groupings": groupings,
        "unique_full_rows_P_R_unit_rhs": len(full_rows),
        "unique_projected_rows_P_R_rhs": len(projected_rows),
        "minimum_slack_on_T158_pentagon": str(best[0]),
        "best_full_row": {
            "P": best[1], "R": best[2], "unit": best[3], "rhs": best[4],
            "maximum_lhs_on_pentagon": str(best[5]),
        },
    }

def build_report(cert):
    source_sha, vertices, pair_tags = validate_source(cert)
    gow = {"c3": audit_gow(3, vertices, pair_tags),
           "c5": audit_gow(5, vertices, pair_tags)}
    g2coc = {
        "c5_n5": audit_g2coc(5, 5, vertices, pair_tags),
        "c5_n7": audit_g2coc(5, 7, vertices, pair_tags),
        "c6_n7": audit_g2coc(6, 7, vertices, pair_tags),
        "c7_n7": audit_g2coc(7, 7, vertices, pair_tags),
    }
    assert gow["c3"] == {
        "groupings": 8400, "unique_projected_rows": 70,
        "minimum_slack_on_T158_pentagon": "0",
        "tight_projected_rows_P_R_rhs": [[2,1,1],[3,0,1],[4,2,2],[6,3,3]],
    }
    assert gow["c5"] == {
        "groupings": 4032, "unique_projected_rows": 49,
        "minimum_slack_on_T158_pentagon": "1/3",
        "tight_projected_rows_P_R_rhs": [],
    }
    expected = {
        "c5_n5": (504,18,18,"2/3",(4,-2,-2,2,"4/3")),
        "c5_n7": (3360,33,21,"4/5",(2,3,-6,3,"11/5")),
        "c6_n7": (2520,34,34,"4/5",(2,3,-6,3,"11/5")),
        "c7_n7": (720,24,24,"1",(1,3,-4,3,"2")),
    }
    for key, want in expected.items():
        row = g2coc[key]
        assert row["groupings"] == want[0]
        assert row["unique_full_rows_P_R_unit_rhs"] == want[1]
        assert row["unique_projected_rows_P_R_rhs"] == want[2]
        assert row["minimum_slack_on_T158_pentagon"] == want[3]
        b = row["best_full_row"]
        assert (b["P"], b["R"], b["unit"], b["rhs"],
                b["maximum_lhs_on_pentagon"]) == want[4]
    return {
        "schema": "generalized-partition-facet-audit-v1",
        "research_ids": ["T160", "E120"],
        "source_g14_pr_certificate_sha256": source_sha,
        "local_vertices": vertices,
        "local_pair_tag_counts": {"P": 12, "R": 3, "unit": 6},
        "T158_pentagon_vertices": [[str(p), str(r)] for p, r in PENTAGON],
        "gow": gow,
        "g2coc": g2coc,
        "totals": {
            "gow_groupings": sum(x["groupings"] for x in gow.values()),
            "g2coc_groupings": sum(x["groupings"] for x in g2coc.values()),
        },
        "status": "PASS_EXACT_SEVEN_POINT_GENERALIZED_PARTITION_FACET_AUDIT",
        "scope": (
            "All GOW and G2COC instances whose nonempty sets fit inside the "
            "complete seven-point T157 P/R/unit core, modulo cyclic rotation "
            "of the side-set labels. No row cuts the exact T158 P/R pentagon. "
            "This does not audit larger grouped windows on Y, alpha>=3 "
            "higher-order cuts, full15 feasibility, or the Hadwiger-Nelson "
            "chromatic number."
        ),
    }

def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=root / "certificates" / "g14_pr_transport_bound.json")
    parser.add_argument("--receipt", type=Path,
                        default=root / "certificates" / "generalized_partition_facet_audit.json")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    report = build_report(read_json(args.source))
    if args.write_receipt:
        args.receipt.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    else:
        assert canonical(read_json(args.receipt)) == canonical(report), (
            "saved generalized-partition-facet receipt differs from exact replay"
        )
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
