"""Exact finite calibration for conditional seven-color rainbow-port research.

Sources: Kostochka-Yancey critical edge bound and Alexeev-Mixon-Parshall
exact planar maximum unit distances u(n) for n <= 21.
General high-girth theorem is Tomon 2026 (external), not this script.
No claim of chi(R^2)=7 or a finite non-six-colorable witness.
"""
from itertools import product
import json


UNIT_MAX_1_TO_21 = (
    0, 1, 3, 5, 7, 9, 12, 14, 18, 20, 23,
    27, 30, 33, 37, 41, 43, 46, 50, 54, 57
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceildiv(a, b):
    return -(-a // b)


def critical_min_edges(n, k=7):
    # Kostochka-Yancey formula for k=7: (10*n - 7)/3.
    require(k == 7 and n >= 7, "scope")
    return ceildiv(10*n - 7, 3)


def small_unit_graph_barrier():
    require(len(UNIT_MAX_1_TO_21) == 21, "unit distance table length")
    table = {}
    for n, u in enumerate(UNIT_MAX_1_TO_21, 1):
        if n >= 7:
            require(critical_min_edges(n) > u, "unexpected possible 7-critical graph")
    # AMP independently establish u(22) <= 61, improving the generic
    # consequence u(22) <= 62 of the exact u(21)=57 value.
    u = 61
    table["22"] = {"certified_upper_unit_edges":u,
                   "min_seven_critical_edges":critical_min_edges(22)}
    for n in range(23, 28):
        u = u * n // (n - 2)
        table[str(n)] = {"certified_upper_unit_edges":u,
                         "min_seven_critical_edges":critical_min_edges(n)}
    for n in range(22,27):
        require(table[str(n)]["min_seven_critical_edges"] >
                table[str(n)]["certified_upper_unit_edges"],
                "barrier < 27 failed")
    require(table["26"] == {"certified_upper_unit_edges":84,
                             "min_seven_critical_edges":85}, "n26 bound")
    require(table["27"] == {"certified_upper_unit_edges":90,
                             "min_seven_critical_edges":88}, "n27 not excluded")
    return {"published_u21":57,"published_u22_upper":61,
            "vertex_lower_for_non_six_unit_graph":27,
            "recurrence_from_u22":table}


def moore_lower_bound(g):
    require(g >= 3, "girth")
    r = g // 2
    if g % 2:
        return 1 + 6 * sum(5**j for j in range(r))
    return 2 * sum(5**j for j in range(r))


def high_girth_consequences():
    expected = {5:37, 6:62, 7:187, 8:312, 9:937, 11:4687}
    for g, n in expected.items():
        require(moore_lower_bound(g) == n, "Moore calculation error")
    return {str(g):n for g,n in expected.items()}


def circle_density_audit():
    # Parameter t in [0,1), unit chord corresponds to t shifted by +/-1/3
    # at radius 1/sqrt(3). 3 arcs of length 1/3 are a proper 3-coloring.
    N = 720
    labels = [3*i//N for i in range(N)]
    require(set(labels) == {0,1,2}, "three arcs")
    require(all(labels[i] != labels[(i+N//3)%N]
                and labels[i] != labels[(i-N//3)%N] for i in range(N)),
            "arc contains a unit chord")
    measure_counts = [labels.count(i) for i in range(3)]
    require(measure_counts == [240,240,240], "arc measure")
    # Exact chord test: squared unit radius r²=1/3, angle=2*pi/3
    # has cosine -1/2, hence chord²=2*r²*(1-cos(angle))=1.
    from fractions import Fraction as Q
    chord_squared=2*Q(1,3)*(1-Q(-1,2))
    require(chord_squared==1, "chord geometry does not match unit distance")
    # The exact measure 2*pi/3 is twice the unsupported threshold pi/3.
    require(Q(2,3)>Q(1,3), "wrong angle density bound")
    return {"circle_radius":"1/sqrt(3)",
            "unit_chord_angular_step":"2*pi/3",
            "valid_three_color_arc_measure_each":"2*pi/3",
            "actual_max_measurable_independent_arc":"2*pi/3",
            "unproved_source_assumption":"strictly less than pi/3",
            "assumption_valid":False,
            "rational_sample_check":N}


def fractionally_colored_from_disk_packing():
    # Only strict *rational envelopes* of the classical geometric density:
    # pi > 3, sqrt(3) < 7/4, so delta=pi/(8sqrt(3)) > 3/14.
    from fractions import Fraction as Q
    require(Q(3) < Q(49,16), "sqrt(3) upper envelope")
    # The pi>3 inequality is a classical analytic input, not proved by code.
    lower_density=Q(3,14)
    require(lower_density>Q(1,5), "nontrivial packing density")
    require(7*lower_density == Q(3,2), "integrality gap lower envelope")
    return {"density":"pi/(8*sqrt(3))",
            "density_strictly_greater_than":str(lower_density),
            "fractional_chromatic_upper":"8*sqrt(3)/pi",
            "hypothetical_chi7_integrality_gap_at_least":"7*pi/(8*sqrt(3))>3/2",
            "pi_greater_than_three_is_external_elementary_input":True}


def rainbow_port_toy():
    # The odd cycle C5 is a complete k=2 analogy of rainbow-port logic:
    # removing v leaves P4; every 2-coloring of P4 gives different colors
    # to the endpoints (the neighbors of removed v).
    path4 = [(0,1),(1,2),(2,3)]
    good = [p for p in product(range(2),repeat=4)
            if all(p[u] != p[v] for u,v in path4)]
    require(len(good)==2 and all(p[0]!=p[3] for p in good), "C5 port")
    # The even C6 has no analogous obstruction; P5 endpoints agree.
    path5 = [(i,i+1) for i in range(4)]
    good_even = [p for p in product(range(2),repeat=5)
                 if all(p[u]!=p[v] for u,v in path5)]
    require(len(good_even)==2 and all(p[0]==p[4] for p in good_even),
            "C6 port")
    return {"C5_minus_center_valid_2_colorings":len(good),
            "C5_port_saturates_two_colors":True,
            "C6_port_saturates_two_colors":False}


def main():
    if not __debug__:
        raise RuntimeError("Optimized mode is not permitted")
    return {
        "status":"PASS_SCOPED_FINITE_EXACT_CHECKS",
        "critical_unit_distance_size":small_unit_graph_barrier(),
        "high_girth_moore_values":high_girth_consequences(),
        "false_external_circle_density_assumption":circle_density_audit(),
        "low_label_port_toy":rainbow_port_toy(),
        "fractional_gap_bound":fractionally_colored_from_disk_packing(),
        "external_inputs_rebuilt_by_script":False,
        "new_general_theorems_lean_formalized":False,
        "full_make_check_executed":False,
        "plane_chromatic_six_or_seven_decided":False,
        "scope":"Exact integer arithmetic and finite combinatorial calibrations only; conditional infinity/high-girth and distance-gadget theorems are written proofs."
    }


if __name__ == "__main__":
    print(json.dumps(main(),ensure_ascii=False,indent=2))
