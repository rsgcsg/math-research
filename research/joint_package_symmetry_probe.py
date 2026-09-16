"""Exact symmetry-package probe; no SAT and no all-coloring negative claim.

The normal entry point independently rebuilds every actual unit edge of Y.
It then exhausts its finite Euclidean isometry group by fixing the centroid
and the image of one noncentral point.  Division in the ambient field is
avoided: a(p-centroid)=b determines the rotation, and multiplication by a
nonzero complex number is injective.  Each actual symmetry pulls back the
whole five-word E083 law; all old full-pattern obligations are rechecked.
"""

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math

from verify_quintic_core_probe import conjugate_twice, digest, filter_map, product_twice
from verify_quintic_multiword_joint import _definitions
from verify_dyadic_mixed_return_joint import _new_definitions
from verify_quintic_tau_union import verify as geometry


def _matrix(table, coefficient, reflection=False):
    columns = []
    for j in range(32):
        basis = [int(i == j) for i in range(32)]
        if reflection:
            basis = conjugate_twice(basis)
        columns.append(product_twice(coefficient, basis, table))
    return [[(j, columns[j][i]) for j in range(32) if columns[j][i]]
            for i in range(32)]


def _apply(matrix, point):
    return tuple(sum(a * point[j] for j, a in row) for row in matrix)


def _exact_mapping(context, definition):
    points = context['points']
    table = context['ring']['table']
    _, coefficient, shift, reflection = definition
    den = math.lcm(*(a.denominator for a in coefficient + shift))
    ic = tuple(int(a * den) for a in coefficient)
    matrix = _matrix(table, ic, reflection)
    # product_twice and (in the reflected case) conjugate_twice contribute
    # exactly these powers of two.
    scale = den * (4 if reflection else 2)
    point_den = math.lcm(*(a.denominator for p in points for a in p))
    integer_points = [tuple(int(a * point_den) for a in p) for p in points]
    lookup = {p: i for i, p in enumerate(integer_points)}
    offset = tuple(int(a * scale * point_den) for a in shift)
    result = []
    for i, p in enumerate(integer_points):
        numerator = tuple(a + b for a, b in zip(_apply(matrix, p), offset))
        if any(a % scale for a in numerator):
            continue
        q = tuple(a // scale for a in numerator)
        if q in lookup:
            result.append((i, lookup[q]))
    assert len({j for _, j in result}) == len(result)
    return result


def _all_symmetries(context):
    """Exhaust all actual affine Euclidean symmetries, not a candidate list."""
    points = context['points']
    table = context['ring']['table']
    n = len(points)
    den = math.lcm(*(a.denominator for p in points for a in p))
    integral = [tuple(int(a * den) for a in p) for p in points]
    total = tuple(sum(p[i] for p in integral) for i in range(32))
    centered = [tuple(n * a - b for a, b in zip(p, total)) for p in integral]
    prime, images, bars = filter_map(table)
    buckets = defaultdict(list)
    for i, p in enumerate(centered):
        if any(p):
            u = sum(a * b for a, b in zip(p, images)) % prime
            v = sum(a * b for a, b in zip(p, bars)) % prime
            buckets[u * v % prime].append(i)
    bucket = min(buckets.values(), key=lambda group: (len(group), group))
    norms = defaultdict(list)
    for i in bucket:
        norm = tuple(product_twice(centered[i], conjugate_twice(centered[i]), table))
        norms[norm].append(i)
    norm_class = min(norms.values(), key=lambda group: (len(group), group))
    anchor_index = norm_class[0]
    anchor = centered[anchor_index]
    left_matrix = _matrix(table, anchor)
    images_left = [_apply(left_matrix, p) for p in centered]
    assert len(set(images_left)) == n
    lookup = {p: i for i, p in enumerate(images_left)}
    automorphisms, rejected = [], []
    for target in norm_class:
        for reflected in (False, True):
            # a*z' = b*z (rotation) or bar(a)*z' = b*bar(z)
            # where all z are centered.  Both equations avoid inverses.
            if reflected:
                lhs = _matrix(table, conjugate_twice(anchor))
                image_lookup = {_apply(lhs, p): i for i, p in enumerate(centered)}
                rhs = _matrix(table, centered[target], reflection=True)
            else:
                image_lookup = lookup
                rhs = _matrix(table, centered[target])
            permutation = []
            missing = None
            for i, p in enumerate(centered):
                q = _apply(rhs, p)
                if q not in image_lookup:
                    missing = i
                    break
                permutation.append(image_lookup[q])
            if missing is None:
                assert sorted(permutation) == list(range(n))
                automorphisms.append(dict(anchor_image=target, reflection=reflected,
                                          permutation=permutation))
            else:
                rejected.append(dict(anchor_image=target, reflection=reflected,
                                     first_missing_point=missing))
    assert any(record['permutation'] == list(range(n)) for record in automorphisms)
    assert len({tuple(record['permutation']) for record in automorphisms}) == len(automorphisms)
    # Optional shorter rigidity witness: two distinct-radius singletons that
    # are noncollinear with the centroid force every Euclidean symmetry to be
    # the identity.  Uniqueness modulo a verified homomorphism is sufficient
    # for uniqueness of the actual algebraic squared radius.
    rigidity_witness = None
    if len(norm_class) == 1:
        for residue, candidates in sorted(buckets.items()):
            if len(candidates) != 1 or candidates[0] == anchor_index:
                continue
            other = candidates[0]
            left = product_twice(anchor, conjugate_twice(centered[other]), table)
            right = product_twice(conjugate_twice(anchor), centered[other], table)
            cross = [a - b for a, b in zip(left, right)]
            if any(cross):
                anchor_residue = next(r for r, group in buckets.items() if anchor_index in group)
                rigidity_witness = dict(point_indices=[anchor_index, other],
                                         radius_residues=[anchor_residue, residue],
                                         residue_class_sizes=[len(buckets[anchor_residue]), 1],
                                         noncollinearity_product_difference=cross)
                assert len(automorphisms) == 1
                break
    edges = set(context['edges'])
    for record in automorphisms:
        perm = record['permutation']
        assert {tuple(sorted((perm[i], perm[j]))) for i, j in edges} == edges
    return automorphisms, dict(centroid_numerator=list(total),
                              centroid_denominator=den * n,
                              filter_prime=prime, modular_bucket=bucket,
                              anchor_index=anchor_index, exact_norm_class=norm_class,
                              rejected_candidates=rejected,
                              two_fixed_points_rigidity_witness=rigidity_witness)


def _pattern(word, indices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in indices)


def _difference(words, mapping):
    source, target = [i for i, _ in mapping], [j for _, j in mapping]
    result = Counter(_pattern(w, source) for w in words)
    result.subtract(_pattern(w, target) for w in words)
    return {p: value for p, value in result.items() if value}


def probe(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    parent, context = geometry(root, geometry_context=True)
    print('Geometry independently rebuilt', parent['geometry'], flush=True)
    source_path = root / 'certificates/quintic_multiword_return_joint.json'
    data = json.loads(source_path.read_text())
    assert data['experiment'] == 'E083' and data['geometry'] == parent['geometry']
    words = data['result']['words']
    assert len(words) == 5
    assert all(len(w) == len(context['points']) and set(w) <= set('01234') for w in words)
    assert all(w[i] != w[j] for w in words for i, j in context['edges'])
    definitions = _definitions(context) + _new_definitions(context)
    maps = [_exact_mapping(context, definition) for definition in definitions]
    assert [digest(mapping) for mapping in maps[:14]] == data['result']['mapping_sha256']
    assert [len(mapping) for mapping in maps[14:]] == [29, 33]
    assert all(not _difference(words, mapping) for mapping in maps[:14])
    automorphisms, group_proof = _all_symmetries(context)
    print('Complete affine Euclidean group size:', len(automorphisms), flush=True)
    packages = []
    for record in automorphisms:
        perm = record['permutation']
        pulled = [''.join(w[j] for j in perm) for w in words]
        assert all(w[i] != w[j] for w in pulled for i, j in context['edges'])
        diffs = [_difference(pulled, mapping) for mapping in maps]
        packages.append(dict(anchor_image=record['anchor_image'],
                             reflection=record['reflection'],
                             permutation_sha256=digest(perm),
                             preserves_old14=not any(diffs[:14]),
                             balanced_domains=[definitions[i][0] for i, d in enumerate(diffs) if not d],
                             differences=diffs,
                             words=pulled))
    admissible = [p for p in packages if p['preserves_old14']]
    assert admissible
    # A direct exact finite-pool separator, if one pattern row has the same
    # strict sign on every eligible package. This is stronger than numerical
    # LP failure, and applies to arbitrary nonnegative real package weights.
    separators = []
    for motion_index in (14, 15):
        patterns = set().union(*(p['differences'][motion_index] for p in admissible))
        for pattern in sorted(patterns):
            values = [p['differences'][motion_index].get(pattern, 0) for p in admissible]
            if min(values) > 0 or max(values) < 0:
                separators.append(dict(motion=definitions[motion_index][0],
                                       pattern=list(pattern), numerators=values,
                                       common_denominator=5))
                break
    report_packages = [{k: v for k, v in p.items() if k not in ('words', 'differences')}
                       for p in packages]
    return dict(status='EXACT_PROBE_COMPLETE',
                source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
                geometry=parent['geometry'],
                group_proof=group_proof,
                automorphism_count=len(automorphisms),
                existing_motion_domains=[dict(motion=d[0], size=len(m), sha256=digest(m))
                                         for d, m in zip(definitions, maps)],
                packages=report_packages,
                admissible_package_count=len(admissible),
                exact_single_row_separators=separators,
                scope=('All actual Euclidean symmetries of this finite Y and their E083 '
                       'whole-package pullbacks only; no SAT, no all-proper-word obstruction, '
                       'no HN bound'))


def verify(root):
    """Recompute the exact result and compare every saved certificate field."""
    root = Path(root)
    actual = probe(root)
    saved = json.loads((root / 'certificates/joint_package_symmetry_probe.json').read_text())
    assert actual == saved
    return actual


if __name__ == '__main__':
    print('PACKAGE_FINAL_JSON=' + json.dumps(verify(Path(__file__).resolve().parents[1]),
                                             separators=(',', ':')))
