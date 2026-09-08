"""Exact full induced-unit-graph probe for the first 1/3 pose pair.

The certificate stores coordinates multiplied by the anchor quadrance d, so
unit distance in the original gate is represented by squared distance d^2.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json

from exact_geometry import distance_squared, sub, add, mul


def point(raw):
    return tuple(tuple(F(x) for x in axis) for axis in raw)


def field_text(a):
    return [str(x) for x in a]


def coordinate_text(p):
    return [field_text(axis) for axis in p]


def colorings(vertices, edges, lists, fixed=None, limit=None):
    """Small MRV backtracker, returning proper colorings as dictionaries."""
    fixed = {} if fixed is None else dict(fixed)
    adjacency = {v: set() for v in vertices}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    out = []

    def visit(assignment):
        if len(assignment) == len(vertices):
            out.append(dict(assignment))
            return limit is not None and len(out) >= limit
        choices = []
        for v in vertices:
            if v in assignment:
                continue
            available = [c for c in lists[v]
                         if all(assignment.get(w) != c for w in adjacency[v])]
            choices.append((len(available), v, available))
        _, v, available = min(choices)
        for c in available:
            assignment[v] = c
            if visit(assignment):
                return True
            del assignment[v]
        return False

    # Fixed values are checked against their lists and each other first.
    for v, c in fixed.items():
        if c not in lists[v]:
            return []
        if any(fixed.get(w) == c for w in adjacency[v]):
            return []
    return (lambda: (visit(dict(fixed)), out)[1])()


def main():
    root = Path(__file__).resolve().parents[1]
    base = json.loads((root / "certificates/spindle_pair_gate.json").read_text())
    fan = json.loads((root / "certificates/repair_pair_fan.json").read_text())
    case = next(c for c in fan["cases"]
                if tuple(map(F, c["certificate"]["squared_anchor_distance"]))
                == (F(1, 3), F(0), F(0), F(0)))
    poses = [
        [point(p) for p in case["certificate"]["scaled_poses"][i]]
        for i in (0, 4)
    ]
    d = tuple(map(F, case["certificate"]["squared_anchor_distance"]))
    unit_scaled = mul(d, d)
    local_edges = {tuple(e) for e in base["induced_edges"]}

    # Coordinate classes expose vertex identifications and shared boundary.
    locations = defaultdict(list)
    for pose, vertices in enumerate(poses):
        for local, coordinate in enumerate(vertices):
            locations[coordinate].append((pose, local))
    collisions = {coord: refs for coord, refs in locations.items() if len(refs) > 1}

    # Build the coordinate-level edge set contributed by the two gates first.
    # This is essential: a cross-pose occurrence can merely be another local
    # name for an edge already present in one gate when boundary points share.
    union_edges = set()
    for pose in range(2):
        for left, right in local_edges:
            union_edges.add(frozenset((poses[pose][left], poses[pose][right])))

    # Every actual unit pair in the 42 labelled occurrences; classify pairs
    # internal to one gate versus genuinely new cross-pose edges.
    all_edges = []
    cross_edges = []
    extra_cross_interior = []
    extra_cross_boundary = []
    for (p, left), (q, right) in combinations(
            [(p, i) for p in range(2) for i in range(21)], 2):
        if p == q:
            continue
        a, b = poses[p][left], poses[q][right]
        if distance_squared(a, b) != unit_scaled:
            continue
        edge = (left, right)
        cross_edges.append(edge)
        geometric_edge = frozenset((a, b))
        if geometric_edge not in union_edges and (left < 7 or right < 7):
            extra_cross_interior.append(edge)
        elif geometric_edge not in union_edges:
            extra_cross_boundary.append(edge)
        union_edges.add(geometric_edge)

    # Canonical union vertices and occurrence map.
    union_vertices = list(locations)
    vertex_of = {p: i for i, p in enumerate(union_vertices)}
    occurrences = [[list(ref) for ref in locations[p]] for p in union_vertices]
    union_edge_indices = sorted({tuple(sorted((vertex_of[a], vertex_of[b])))
                                 for a, b in union_edges})

    # Boundary lists and the explicitly requested reversed pair orientations.
    # Pose 0 gets (3,4) on the root pair and (0,4) on every other pair;
    # pose 1 reverses each pair.  The two shared boundary points consequently
    # receive the same color from both occurrences.
    boundary_occurrence_colors = {}
    for pose in range(2):
        for pair_number, (left, right) in enumerate(base["boundary_pairs"]):
            palette = (3, 4) if pair_number == 0 else (0, 4)
            values = palette if pose == 0 else palette[::-1]
            boundary_occurrence_colors[(pose, left)] = values[0]
            boundary_occurrence_colors[(pose, right)] = values[1]
    boundary_colors = {}
    for pose_local, c in boundary_occurrence_colors.items():
        boundary_colors[vertex_of[poses[pose_local[0]][pose_local[1]]]] = c
    assert len(boundary_colors) == 26
    assert boundary_colors[vertex_of[poses[0][9]]] == boundary_colors[vertex_of[poses[1][10]]]
    assert boundary_colors[vertex_of[poses[0][15]]] == boundary_colors[vertex_of[poses[1][16]]]
    boundary_edges = [(a, b) for a, b in union_edge_indices
                      if a in boundary_colors and b in boundary_colors]
    assert all(boundary_colors[a] != boundary_colors[b] for a, b in boundary_edges)

    # Standalone spindle list-colorings, one per pose.  Local 0 has
    # {0,1,2}; locals 1..6 have {1,2,3}.
    spindle_edges = [(a, b) for a, b in local_edges if a < 7 and b < 7]
    spindle_lists = {0: (0, 1, 2), **{v: (1, 2, 3) for v in range(1, 7)}}
    standalone = []
    standalone_all = []
    for pose in range(2):
        all_witnesses = colorings(range(7), spindle_edges, spindle_lists)
        assert all_witnesses and all_witnesses[0][0] == 0
        standalone_all.append(all_witnesses)
        standalone.append(all_witnesses[0])

    # Unrestricted proper 4-coloring of the full 40-point induced graph.
    full_lists = {v: tuple(range(4)) for v in range(len(union_vertices))}
    full = colorings(range(len(union_vertices)), union_edge_indices, full_lists, limit=1)
    assert full

    # The requested coupled list instance fixes the boundary colors and uses
    # the corresponding spindle lists on both gates.  Its two roots are
    # joined by the genuine cross edge (0,0), so it has no extension.
    joint_lists = {v: tuple(range(4)) for v in range(len(union_vertices))}
    for pose in range(2):
        for local, values in spindle_lists.items():
            joint_lists[vertex_of[poses[pose][local]]] = values
    joint = colorings(range(len(union_vertices)), union_edge_indices, joint_lists,
                      fixed=boundary_colors, limit=1)
    root_cross = (vertex_of[poses[0][0]], vertex_of[poses[1][0]])
    assert tuple(sorted(root_cross)) in union_edge_indices and not joint

    # Exact quadrance for every one of the 780 distinct vertex pairs.
    all_pair_quadrances = [
        {"pair": [i, j], "quadrance": field_text(
            distance_squared(union_vertices[i], union_vertices[j]))}
        for i, j in combinations(range(len(union_vertices)), 2)
    ]
    certificate = {
        "schema": 1,
        "case": "squared_anchor_distance_1/3_pose_pair_0_4",
        "coordinate_scale_squared": field_text(d),
        "coordinate_scale": "anchor quadrance d=1/3; stored coordinates are d times actual coordinates",
        "vertices": [coordinate_text(p) for p in union_vertices],
        "occurrences": occurrences,
        "shared_boundary_occurrences": [refs for refs in collisions.values()],
        "unit_edges": [list(e) for e in union_edge_indices],
        "unit_edge_count": len(union_edge_indices),
        "boundary_unit_edges": [list(e) for e in boundary_edges],
        "boundary_coloring": {str(v): c for v, c in sorted(boundary_colors.items())},
        "boundary_occurrence_coloring": {f"{p}:{i}": c
                                          for (p, i), c in sorted(boundary_occurrence_colors.items())},
        "standalone_spindle_lists": {str(v): list(cs) for v, cs in spindle_lists.items()},
        "standalone_spindle_witnesses": standalone,
        "standalone_spindle_counts": [len(ws) for ws in standalone_all],
        "standalone_root_support": [sorted({w[0] for w in ws}) for ws in standalone_all],
        "joint_fixed_boundary_list_colorings": 0,
        "joint_failure_edge": list(sorted(root_cross)),
        "full_unrestricted_4_coloring": {str(v): c for v, c in full[0].items()},
        "all_pair_quadrances": all_pair_quadrances,
    }
    target = root / "certificates/coupled_gate.json"
    target.write_text(json.dumps(certificate, indent=2) + "\n")
    print(json.dumps({
        "case": "squared_anchor_distance_1/3",
        "poses": case["certificate"]["labels"][0:1] + case["certificate"]["labels"][4:5],
        "occurrences": 42,
        "distinct_union_vertices": len(locations),
        "collisions": {str(k): v for k, v in collisions.items()},
        "shared_boundary_local_indices": [v for v in collisions.values()
                                           if all(local >= 7 for _, local in v)],
        "cross_unit_edges_local_indices": cross_edges,
        "extra_cross_interior_local_indices": extra_cross_interior,
        "extra_cross_boundary_local_indices": extra_cross_boundary,
        "extra_cross_interior_count": len(extra_cross_interior),
        "within_gate_edges_each": len(local_edges),
        "distinct_union_unit_edges": len(union_edges),
        "certificate": str(target),
        "all_unique_physical_pairs": len(all_pair_quadrances),
        "standalone_root_support": [sorted({w[0] for w in ws}) for ws in standalone_all],
        "joint_fixed_boundary_list_colorings": 0,
        "joint_failure_edge": list(sorted(root_cross)),
        "full_4_colorable": bool(full),
        "shape": "single cross-pose edge" if len(extra_cross_interior) == 1
                 else "multiple cross-pose edges",
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
