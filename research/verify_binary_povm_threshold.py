"""Independent exact graph and rational-effect certificates for R158-V.

No optimizer is used. General graph/dimension claims use the written proof.
"""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import sys
from binary_povm_arithmetic import (
    F, ZERO, z, ident, add, scale, mm, norm2, formula_check,
    exact_identity_samples, clifford_samples, require,
)

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'certificates/binary_povm_threshold.json'


def hs_edges():
    edges = set()
    def edge(u, v):
        require(u != v, 'loop')
        edges.add(tuple(sorted((u, v))))
    for h in range(5):
        for j in range(5):
            edge(5*h+j, 5*h+(j+1) % 5)
    for i in range(5):
        for k in range(5):
            edge(25+5*i+k, 25+5*i+(k+2) % 5)
    for h, j, i in product(range(5), repeat=3):
        edge(5*h+j, 25+5*i+(h*i+j) % 5)
    return [list(e) for e in sorted(edges)]


def matmul_int(a, b):
    return [[sum(x*y for x, y in zip(ar, bc)) for bc in zip(*b)] for ar in a]


def hs_verify(data):
    require(data['n'] == 50 and data['edges'] == hs_edges(), 'HS edge list differs')
    a = [[0]*50 for _ in range(50)]
    for u, v in data['edges']:
        a[u][v] = a[v][u] = 1
    require(len(data['edges']) == 175 and all(sum(row) == 7 for row in a), 'HS degree/count')
    a2 = matmul_int(a, a)
    require(all(a2[i][j] == 6*(i == j)-a[i][j]+1 for i in range(50) for j in range(50)), 'HS SRG identity')
    triangles = sum(a[i][j]*a[i][k]*a[j][k] for i in range(50) for j in range(i) for k in range(j))
    require(triangles == 0, 'HS triangle detected')
    b = [[5*a[i][j]+15*(i == j)-1 for j in range(50)] for i in range(50)]
    b2 = matmul_int(b, b)
    require(all(125*(2*a[i][j]+7*(i == j)) == 125*(i == j)+2*b2[i][j]+50
                for i in range(50) for j in range(50)), 'integer PSD certificate')
    c = [[20*(i == j)-10*a[i][j]+1 for j in range(50)] for i in range(50)]
    c2 = matmul_int(c, c)
    require(all(c2[i][j] == 50*c[i][j] for i in range(50) for j in range(50)), 'Gram square certificate')
    require(all(c[i][i] == 21 for i in range(50)), 'Gram normalization')
    require(all(F(c[u][v], 21) == -F(3, 7) for u, v in data['edges']), 'Gram edge value')
    expected = dict(edges=175, vertices=50, degree=7, triangles=0,
                    integer_sos_entries=2500, gram_square_entries=2500,
                    vector_chromatic_number='10/3', normalized_binary_optimum='1/4',
                    stability_constant=700, plane_unit_distance_realization_claimed=False)
    require(data['claims'] == expected, 'HS claim fields differ')
    return expected


DIRECTIONS = [['1', '0'], ['-4/5', '3/5'], ['7/25', '-24/25'],
              ['7/25', '24/25'], ['-4/5', '-3/5']]


def diagonal(values):
    return tuple(tuple(z(values[i]) if i == j else ZERO for j in range(len(values)))
                 for i in range(len(values)))


def c5_verify(data):
    require(data['directions'] == DIRECTIONS, 'C5 directions changed')
    vectors = [tuple(map(F, row)) for row in data['directions']]
    require(all(sum(x*x for x in v) == 1 for v in vectors), 'C5 sphere equation')
    require(data['t'] == '3/8', 'C5 effect amplitude')
    t = F(data['t'])
    require(0 < t < F(1, 2), 'effect eigenvalues not in (0,1)')
    effects = [((z(F(1, 2)+t*x), z(t*y)), (z(t*y), z(F(1, 2)-t*x))) for x, y in vectors]
    diagonal_effects = [diagonal([F(1, 2)+t*x, F(1, 2)+t*y,
                                 F(1, 2)-t*x, F(1, 2)-t*y]) for x, y in vectors]
    defects, diagonal_defects = [], []
    for i in range(5):
        j = (i+1) % 5
        require(sum(x*y for x, y in zip(vectors[i], vectors[j])) <= -F(4, 5), 'C5 vector edge')
        for family, out in [(effects, defects), (diagonal_effects, diagonal_defects)]:
            ident_n = ident(len(family[0]))
            for sign in (False, True):
                a, b = family[i], family[j]
                if sign:
                    a, b = add(ident_n, scale(-1, a)), add(ident_n, scale(-1, b))
                out.append(norm2(mm(a, b)))
    require(max(defects) == F(821, 10240) < F(2, 16), 'C5 2D strict certificate')
    require(max(diagonal_defects) < F(4, 16), 'C5 commuting strict certificate')
    require(data['qubit_max_squared_error'] == str(max(defects)), 'C5 declared defect')
    require(data['diagonal4_max_squared_error'] == str(max(diagonal_defects)), 'C5 declared diagonal defect')
    return dict(vertices=5, matrix_products_checked=20, qubit_max_squared_error=str(max(defects)),
                qubit_uniform_squared_error='1/8', diagonal4_max_squared_error=str(max(diagonal_defects)),
                diagonal4_uniform_squared_error='1/4', optimality_claimed=False)


def boundary_checks():
    # A three-outcome exact coloring on C3 falsifies the unqualified extension.
    checks = 0
    for t in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
        es = [[(1-t)/3+t*(i == v) for i in range(3)] for v in range(3)]
        require(all(sum(v) == 1 and min(v) >= 0 for v in es), 'three outcome normalization')
        actual = max(es[u][i]*es[v][i] for u, v in [(0,1),(1,2),(2,0)] for i in range(3))
        require(actual == (1+t-2*t*t)/9, 'three-outcome path formula')
        checks += 1
    # Exact arithmetic for the rational minimizer used in the general lower bound.
    bounds = 0
    for numerator in range(20, 31):
        kappa = F(numerator, 10)
        s = -1/(kappa-1)
        zstar = (kappa-1)*(3-kappa)/4
        require(0 <= zstar <= F(1, 4), 'bound minimizer out of range')
        value = F(1,16)+zstar*(F(1,2)+s)+zstar*zstar*s*s
        require(value == (kappa-2)*(4-kappa)/16, 'lower-bound exact simplification')
        upper = (kappa-2)/(4*(kappa-1)**2)
        require(value <= upper <= F(1,16), 'lower/upper ordering')
        bounds += 1
    return dict(three_outcome_path_parameters=checks, rational_kappa_calibrations=bounds)


def unique_keys(pairs):
    d = {}
    for k, v in pairs:
        require(k not in d, 'duplicate JSON key')
        d[k] = v
    return d


def verify(data):
    require(set(data) == {'schema', 'hoffman_singleton', 'c5'}, 'certificate keys')
    require(data['schema'] == 'hn-binary-povm-v1', 'certificate schema')
    return dict(hoffman_singleton=hs_verify(data['hoffman_singleton']), c5=c5_verify(data['c5']))


def self_tests(data):
    bads = []
    b = deepcopy(data); b['hoffman_singleton']['edges'].pop(); bads.append(b)
    b = deepcopy(data); b['hoffman_singleton']['edges'][0] = [0, 0]; bads.append(b)
    b = deepcopy(data); b['hoffman_singleton']['claims']['stability_constant'] = 699; bads.append(b)
    b = deepcopy(data); b['hoffman_singleton']['claims']['plane_unit_distance_realization_claimed'] = True; bads.append(b)
    b = deepcopy(data); b['c5']['directions'][0][0] = '2'; bads.append(b)
    b = deepcopy(data); b['c5']['t'] = '1/2'; bads.append(b)
    b = deepcopy(data); b['c5']['qubit_max_squared_error'] = '0'; bads.append(b)
    b = deepcopy(data); b['schema'] = 'unrecognized'; bads.append(b)
    for b in bads:
        try:
            verify(b)
        except ValueError:
            continue
        raise ValueError('mutated certificate accepted')
    rejected = len(bads)
    try:
        json.loads('{"same":0,"same":1}', object_pairs_hook=unique_keys)
    except ValueError:
        rejected += 1
    else:
        raise ValueError('duplicate JSON keys accepted')
    try:
        formula_check(((z(0), z(1)), (z(0), z(0))), ident(2))
    except ValueError:
        rejected += 1
    else:
        raise ValueError('non-Hermitian sample accepted')
    return rejected


def main():
    if not __debug__:
        raise RuntimeError('Binary POVM verifier requires non-optimized Python')
    require(sys.argv[1:] in ([], ['--self-test']), 'unsupported argument')
    data = json.loads(CERT.read_text(), object_pairs_hook=unique_keys)
    report = dict(status='PASS_EXACT_FINITE_EVIDENCE', certificate=verify(data),
                  noncommutative_identity=exact_identity_samples(),
                  clifford=clifford_samples(), boundary_checks=boundary_checks(),
                  general_theorem_lean_formalized=False, full15_decided=False,
                  new_hn_bound=False,
                  scope='Exact stored graph and rational POVM witnesses; finite formula calibration. '
                        'General graph/dimension classification and the conic alternative use the written proof.')
    if sys.argv[1:]:
        report['mutations_rejected'] = self_tests(data)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
