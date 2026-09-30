#!/usr/bin/env python3
"""Exact bounded coupling audit for certified E/P/Q/R pairs on the fixed Y.

This reconstructs quotient and short pair-path facts from the pinned published
pair-node lists, counts selected P/Q/R triangles, and checks the C027-style
alpha<=2 matching-window family with two independent clique enumerators.
It does not solve full15 or enumerate the full Q-augmented BW family.
"""
import argparse
from collections import Counter, defaultdict, deque
from itertools import combinations, product
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')

import verify_pr_matching_window_ceiling as matching

ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = ROOT / 'certificates/q_pr_coupling_audit.json'
Q_BASIS = '757a6f62edfb5285b9fde82f55c93454abd6e6a5b1985f3838d4c2a93e003534'
GEOMETRY = matching.GEOMETRY
EXPECTED_TRIANGLES = {
    'PPP': 1080, 'PPR': 1380, 'PRR': 68,
    'QQQ': 280, 'QRR': 1560, 'RRR': 720,
}
EXPECTED_ABSENT_TRIANGLES = ['PPQ', 'PQQ', 'PQR', 'QQR']


def normalized_pairs(raw_pairs):
    pairs = [tuple(sorted(map(int, pair))) for pair in raw_pairs]
    assert all(len(pair) == 2 and pair[0] < pair[1] for pair in pairs)
    assert len(pairs) == len(set(pairs))
    return set(pairs)


class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b] or (self.size[a] == self.size[b] and a > b):
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        return True

    def roots(self):
        return [self.find(v) for v in range(len(self.parent))]


def quotient_edges(pairs, roots):
    loops = []
    representatives = defaultdict(list)
    for a, b in sorted(pairs):
        x, y = roots[a], roots[b]
        if x == y:
            loops.append((a, b))
        else:
            representatives[tuple(sorted((x, y)))].append((a, b))
    return loops, representatives


def pair_list_sha(pairs):
    return matching.digest([list(e) for e in sorted(pairs)])


def quotient_distances(n, roots, edge_representatives, source_pairs):
    """Count shortest R-edge distances after Q contraction; return witness paths."""
    adj = defaultdict(set)
    representative = {}
    for edge, actual_pairs in edge_representatives.items():
        a, b = edge
        adj[a].add(b)
        adj[b].add(a)
        representative[edge] = min(actual_pairs)

    cache = {}

    def bfs(source):
        if source in cache:
            return cache[source]
        previous = {source: None}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in sorted(adj.get(u, ())):
                if v not in previous:
                    previous[v] = (u, tuple(sorted((u, v))))
                    queue.append(v)
        cache[source] = previous
        return previous

    def unwind(previous, target):
        edges = []
        nodes = [target]
        current = target
        while previous[current] is not None:
            current, edge = previous[current]
            edges.append(edge)
            nodes.append(current)
        return list(reversed(nodes)), list(reversed(edges))

    counts = Counter()
    witnesses = {}
    for a, b in sorted(source_pairs):
        x, y = roots[a], roots[b]
        if x == y:
            distance = 0
            previous = None
        else:
            previous = bfs(x)
            distance = None if y not in previous else len(unwind(previous, y)[1])
        key = 'infinity' if distance is None else str(distance)
        counts[key] += 1
        if key in witnesses and [a, b] >= witnesses[key]['pair']:
            continue
        if distance is None:
            witnesses[key] = {'pair': [a, b], 'q_classes': [x, y]}
        elif distance == 0:
            witnesses[key] = {'pair': [a, b], 'q_class': x}
        else:
            nodes, path_edges = unwind(previous, y)
            witnesses[key] = {
                'pair': [a, b],
                'q_classes': [x, y],
                'r_quotient_path_classes': nodes,
                'r_actual_pair_representatives': [list(representative[e]) for e in path_edges],
            }
    return dict(sorted(counts.items())), dict(sorted(witnesses.items()))


def triangle_census(P, Q, R):
    kind = {e: 'P' for e in P}
    kind.update({e: 'Q' for e in Q})
    kind.update({e: 'R' for e in R})
    adj = defaultdict(set)
    for a, b in kind:
        adj[a].add(b)
        adj[b].add(a)
    counts = Counter()
    witnesses = {}
    for a in sorted(adj):
        for b in sorted(v for v in adj[a] if v > a):
            for c in sorted(v for v in adj[a] & adj[b] if v > b):
                profile = ''.join(sorted((
                    kind[tuple(sorted((a, b)))],
                    kind[tuple(sorted((a, c)))],
                    kind[tuple(sorted((b, c)))],
                )))
                counts[profile] += 1
                witnesses.setdefault(profile, {
                    'vertices': [a, b, c],
                    'edges': [
                        {'pair': [a, b], 'type': kind[tuple(sorted((a, b)))]},
                        {'pair': [a, c], 'type': kind[tuple(sorted((a, c)))]},
                        {'pair': [b, c], 'type': kind[tuple(sorted((b, c)))]},
                    ],
                })
    assert dict(sorted(counts.items())) == EXPECTED_TRIANGLES
    assert sorted(set(''.join(p) for p in product('PQR', repeat=3) if ''.join(p) == ''.join(sorted(p)))-set(counts)) == EXPECTED_ABSENT_TRIANGLES

    qrr = witnesses['QRR']
    assert qrr['vertices'] == [31, 35, 873]
    assert qrr['edges'] == [
        {'pair': [31, 35], 'type': 'R'},
        {'pair': [31, 873], 'type': 'R'},
        {'pair': [35, 873], 'type': 'Q'},
    ]
    # The partition inequality is e_R(31,35)+e_R(31,873)-e_Q(35,873)<=1.
    for xa, xb, xc in product((0, 1), repeat=3):
        assert xa * xb + xa * xc - xb * xc <= 1
        # The same weak triangle bound holds for a single independent-set moment.
        assert xa * xb + xa * xc - xb * xc <= xa

    return {
        'counts': dict(sorted(counts.items())),
        'absent_profiles': EXPECTED_ABSENT_TRIANGLES,
        'witnesses': dict(sorted(witnesses.items())),
        'QRR_inequality': '2r - q <= 1',
        'QRR_binary_checks': 8,
        'QRR_single_independent_set_pointwise_checks': 8,
    }


def is_bipartite(vertices, edges):
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    color = {}
    for source in vertices:
        if source in color:
            continue
        color[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in sorted(adj[u]):
                if v not in color:
                    color[v] = color[u] ^ 1
                    queue.append(v)
                else:
                    assert color[v] != color[u]
    return True


def matching_window_census(n, E, P, Q, R):
    support = E | P | Q | R
    adj = [set() for _ in range(n)]
    for a, b in support:
        adj[a].add(b)
        adj[b].add(a)

    # Reuse the two exact algorithms already independently used for the P/R census.
    cliques = matching.ordered_cliques(adj)
    maximal = matching.maximal_cliques(adj)
    by_maximal = {j: set() for j in range(2, 8)}
    for vertices in maximal:
        for j in by_maximal:
            by_maximal[j].update(combinations(vertices, j))
    assert cliques == by_maximal

    profiles = Counter()
    alpha2_windows = []
    q_containing_5_cliques = 0
    for vertices in sorted(cliques[5]):
        pairs = [tuple(sorted(pair)) for pair in combinations(vertices, 2)]
        if any(e in Q for e in pairs):
            q_containing_5_cliques += 1
        alpha_le_two = all(
            any(tuple(sorted(e)) in E for e in combinations(triple, 2))
            for triple in combinations(vertices, 3)
        )
        if not alpha_le_two:
            continue
        p_count = sum(e in P for e in pairs)
        q_count = sum(e in Q for e in pairs)
        r_count = sum(e in R for e in pairs)
        profiles[(p_count, q_count, r_count)] += 1
        nonunit = [e for e in pairs if e not in E]
        degree = Counter(v for e in nonunit for v in e)
        assert len(nonunit) == 6
        assert sorted(degree.values()) == [2, 2, 2, 3, 3]
        assert is_bipartite(vertices, nonunit)
        local_adj = {v: set() for v in vertices}
        for x, y in nonunit:
            local_adj[x].add(y)
            local_adj[y].add(x)
        high = {v for v in vertices if len(local_adj[v]) == 3}
        low = set(vertices) - high
        assert len(high) == 2 and len(low) == 3
        assert all(local_adj[v] == low for v in high)
        assert all(local_adj[v] == high for v in low)
        alpha2_windows.append(vertices)

    assert len(cliques[5]) == 11160
    assert len(alpha2_windows) == 2280
    assert profiles == Counter({(4, 0, 2): 2280})
    maximal_counts = Counter(map(len, maximal))
    clique_hashes = {
        str(j): matching.digest(sorted(cliques[j]))
        for j in range(2, 8)
    }
    return {
        'support_edges': len(support),
        'clique_algorithms': [
            'ordered common-neighbor recursion',
            'pivoting Bron-Kerbosch plus deduplicated subsets',
        ],
        'clique_counts_by_size': {str(j): len(cliques[j]) for j in range(2, 8)},
        'clique_set_sha256_by_size': clique_hashes,
        'maximal_clique_size_counts': {str(j): v for j, v in sorted(maximal_counts.items())},
        'all_5_clique_algorithms_agree': cliques[5] == by_maximal[5],
        'all_5_cliques': len(cliques[5]),
        'q_containing_5_cliques': q_containing_5_cliques,
        'alpha_le_2_5_windows': len(alpha2_windows),
        'alpha_le_2_profile_counts': {
            f'{p}P+{q}Q+{r}R': count
            for (p, q, r), count in sorted(profiles.items())
        },
        'C027_matching_cut': '4p + 2r <= 2, equivalently 2p + r <= 1; this is already a facet of H and contains no Q coordinate',
        'scope': 'All 5-cliques of E∪P∪Q∪R, filtered for alpha(E[W])<=2. Each eligible nonunit graph is K2,3, hence bipartite; no C027 C5 blossom window contains Q.',
    }


def build_report():
    g = matching.read(ROOT / 'certificates/Y_full_geometry.json.gz')
    pb = matching.read(ROOT / 'certificates/g14_pair_orbit_basis.json.gz')
    rb = matching.read(ROOT / 'certificates/g14_r_pair_orbit_basis.json.gz')
    n, E, P, R = matching.validate_inputs(g, pb, rb)

    q0 = dict(pb)
    q_hash = q0.pop('basis_sha256')
    assert q_hash == Q_BASIS == matching.digest(q0)
    assert pb['geometry_semantic_sha256'] == GEOMETRY
    Q = normalized_pairs(pb['orbit_nodes_by_grade']['2'])
    assert len(Q) == 780 and not (Q & (E | P | R))
    assert all(0 <= a < b < n for a, b in E | P | Q | R)

    # Q-only contraction and quotient edge overlap checks.
    q_dsu = DSU(n)
    for a, b in sorted(Q):
        q_dsu.union(a, b)
    q_roots = q_dsu.roots()
    q_classes = defaultdict(list)
    for vertex, representative in enumerate(q_roots):
        q_classes[representative].append(vertex)
    q_unit_loops, _ = quotient_edges(E, q_roots)
    q_p_loops, p_q_edges = quotient_edges(P, q_roots)
    q_r_loops, r_q_edges = quotient_edges(R, q_roots)
    q_e_loops, e_q_edges = quotient_edges(E, q_roots)
    assert (len(q_classes), n - len(q_classes)) == (9577, 500)
    assert not q_unit_loops and not q_p_loops and not q_r_loops
    q_hist = Counter(map(len, q_classes.values()))
    assert dict(sorted(q_hist.items())) == {1: 9359, 3: 158, 4: 58, 6: 2}
    quotient_intersections = {
        'P_R': len(set(p_q_edges) & set(r_q_edges)),
        'P_E': len(set(p_q_edges) & set(e_q_edges)),
        'R_E': len(set(r_q_edges) & set(e_q_edges)),
    }
    assert quotient_intersections == {'P_R': 0, 'P_E': 0, 'R_E': 0}
    assert (len(e_q_edges), len(p_q_edges), len(r_q_edges)) == (48706, 780, 332)

    # Q∪R contraction. On p=0, the collapsed P pair events are additional
    # different-color conflicts, not unit-edge loops.
    qr_dsu = DSU(n)
    for a, b in sorted(Q | R):
        qr_dsu.union(a, b)
    qr_roots = qr_dsu.roots()
    qr_classes = len(set(qr_roots))
    e_qr_loops, _ = quotient_edges(E, qr_roots)
    p_qr_loops, _ = quotient_edges(P, qr_roots)
    assert (qr_classes, n - qr_classes) == (9341, 736)
    assert len(e_qr_loops) == 120 and len(p_qr_loops) == 188
    assert len(e_qr_loops) + len(p_qr_loops) == 308
    # Exact short paths use only event pairs from the certified R component.
    unit_path = [
        (238, 229), (229, 4641), (4641, 305),
    ]
    p_path = [(229, 4641), (4641, 305)]
    assert (238, 305) in E and all(tuple(sorted(e)) in R for e in unit_path)
    assert (229, 305) in P and all(tuple(sorted(e)) in R for e in p_path)
    assert len({qr_roots[v] for v in [238, 229, 4641, 305]}) == 1

    # Full R graph on Q-classes: shortest paths are by number of R pair edges,
    # so arbitrarily long Q paths inside a class cost zero as required.
    unit_r_distances, unit_r_witnesses = quotient_distances(n, q_roots, r_q_edges, E)
    p_r_distances, p_r_witnesses = quotient_distances(n, q_roots, r_q_edges, P)
    assert unit_r_distances == {'3': 72, '4': 48, 'infinity': 49738}
    assert p_r_distances == {'2': 76, '3': 64, '4': 48, 'infinity': 1672}
    assert unit_r_witnesses['3']['pair'] == [238, 305]
    assert p_r_witnesses['2']['pair'] == [229, 305]

    triangles = triangle_census(P, Q, R)
    matching_windows = matching_window_census(n, E, P, Q, R)

    # Exact check that the previous P/R polygon H remains available at q=1
    # for the inspected path/triangle inequalities. This is projection-only,
    # not a claim of an actual full-Y law at q=1.
    H = matching.VERTICES
    assert all(3 * p <= 1 and 2 * p + r <= 1 and 2 * r - p <= 1
               and 12 * p + 3 * r >= 2 for p, r in H)
    assert all(2 * r - 1 <= 1 for p, r in H)

    return {
        'schema': 'q-pr-coupling-audit-v1',
        'research_id': 'E119',
        'status': 'PASS_EXACT_BOUNDED_Q_PR_COUPLING_AUDIT',
        'inputs': {
            'geometry_semantic_sha256': GEOMETRY,
            'P_Q_basis_sha256': Q_BASIS,
            'R_candidate_sha256': matching.R_BASIS,
            'vertices': n,
            'actual_unit_edges_E': len(E),
            'selected_P_pairs': len(P),
            'selected_Q_pairs': len(Q),
            'selected_R_pairs': len(R),
        },
        'Q_only_contraction': {
            'classes': len(q_classes),
            'merges': n - len(q_classes),
            'class_size_histogram': {str(k): v for k, v in sorted(q_hist.items())},
            'unit_loops': len(q_unit_loops),
            'collapsed_P_pairs': len(q_p_loops),
            'collapsed_R_pairs': len(q_r_loops),
            'quotient_pair_edge_counts': {
                'E': len(e_q_edges), 'P': len(p_q_edges), 'R': len(r_q_edges),
            },
            'quotient_pair_intersections': quotient_intersections,
        },
        'Q_union_R_contraction': {
            'classes': qr_classes,
            'merges': n - qr_classes,
            'actual_unit_edge_loops': len(e_qr_loops),
            'P_different_pair_loops_on_p_zero_face': len(p_qr_loops),
            'combined_conflicts_on_p_zero_face': len(e_qr_loops) + len(p_qr_loops),
            'unit_loop_pairs_sha256': pair_list_sha(e_qr_loops),
            'collapsed_P_pairs_sha256': pair_list_sha(p_qr_loops),
            'unit_loop_path_witness': {
                'unit_edge': [238, 305], 'R_equal_pairs': [list(e) for e in unit_path],
            },
            'P_loop_path_witness': {
                'P_pair': [229, 305], 'R_equal_pairs': [list(e) for e in p_path],
            },
            'scope_note': '308 counts 120 E loops plus 188 P inequalities only on p=0; it is not 308 unit-edge loops.',
        },
        'shortest_R_paths_after_Q_contraction': {
            'actual_unit_pair_endpoint_distances': {
                'distance_counts': unit_r_distances,
                'witnesses': unit_r_witnesses,
            },
            'P_pair_endpoint_distances': {
                'distance_counts': p_r_distances,
                'witnesses': p_r_witnesses,
            },
            'interpretation': 'No unit endpoints have R-distance 1 or 2 after Q contraction; the minimum is 3. P endpoints have no R-distance-1 pair; distance 2 yields only 2r-p<=1, already in H.',
        },
        'selected_pair_event_triangles': triangles,
        'C027_matching_window_test': matching_windows,
        'bounded_conclusion': {
            'QRR': '2r-q<=1 is a genuine Q/R marginal coupling, but the pointwise binary check shows it is the ordinary triangle inequality and is satisfied by the single-independent-set moment relaxation.',
            'projection': 'The inspected ordinary pair-path cuts and alpha<=2 C027/Edmonds matching windows do not shrink H at q=1. This is not a full Q-augmented BW proof or a full15 result.',
            'unresolved': ['full Q-augmented BW odd-cycle family', 'higher-order partition cuts and alpha>=3 windows', 'full15 joint-law feasibility'],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true',
                        help='write the deterministic certificate instead of comparing it')
    args = parser.parse_args()
    report = build_report()
    if args.write:
        CERTIFICATE.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    else:
        assert matching.canonical(matching.read(CERTIFICATE)) == matching.canonical(report), \
            'Saved Q/P/R coupling audit certificate differs from exact replay'
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
