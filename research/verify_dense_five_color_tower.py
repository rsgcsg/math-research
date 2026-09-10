"""Independent local/numerical calibrations for T083, standard library only.

This does NOT construct or certify an infinite class-field tower. Its existence
uses the stated external class-field and Golod-Shafarevich inputs in the proof.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import json
import math


T = (3, 5, 11, 23, 31, 37, 47, 53)
P = 40429
K_EXPONENT = 16384


def prime(n):
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def local_parameters():
    assert len(T) == 8 and len(set(T)) == 8
    assert all(prime(q) and q % 2 for q in T)
    assert sum(q % 4 == 3 for q in T) == 5
    discriminant_factor = math.prod(T)
    assert discriminant_factor == 10842986715
    assert discriminant_factor % 4 == 3
    assert prime(P) and P % 4 == 1 and P not in T
    assert all(pow(q, (P - 1) // 2, P) == 1 for q in T)
    roots11 = {}
    lifts = 0
    for q in T:
        if q == 11:
            continue
        roots = [a for a in range(11) if a * a % 11 == q % 11]
        assert len(roots) == 2 and all(2 * a % 11 for a in roots)
        roots11[q] = roots
        a, modulus = roots[0], 11
        for _ in range(8):
            correction = (-(a * a - q) // modulus) * pow(2 * a, -1, 11) % 11
            a += correction * modulus
            modulus *= 11
            assert (a * a - q) % modulus == 0
            lifts += 1
    assert pow(discriminant_factor // 11, 5, 11) == 1
    # One Q-prime above ramified 11 and two above split P are cut.
    generators_lower_bound = len(T) - 1
    finite_split_places = 1 + 2
    all_split_places = 2 + finite_split_places  # Include both real places.
    theta = 1  # mu_2 is contained in Q0 and the ramification set is empty.
    relation_excess = all_split_places - 1 + theta
    assert generators_lower_bound == 7 and relation_excess == 5
    assert 4 * (generators_lower_bound + relation_excess) < generators_lower_bound ** 2
    # Identity establishing the GS inequality for every integer d >= 7.
    for d in range(7, 33):
        assert d * d - 4 * d - 20 == (d - 7) * (d + 3) + 1 > 0
    return discriminant_factor, roots11, lifts


def exponent_bound(discriminant_factor):
    # lambda=2*sqrt(D)<220000, sqrt(lambda)<470, log(lambda)<13.
    assert discriminant_factor < 110000 ** 2
    assert 220000 < 470 ** 2
    assert 220000 * 3 ** 13 < 8 ** 13
    # e > 8/3, e < 3 and pi > 3 yield
    # 2e sqrt(lambda) log(lambda)/pi < 2*470*13 = 12220.
    upper_norm_factor = 2 * 470 * 13
    assert upper_norm_factor == 12220 < K_EXPONENT + 1
    numerator_lower = Q(K_EXPONENT + 1 - upper_norm_factor,
                        2 * (K_EXPONENT + 1))
    assert numerator_lower == Q(4165, 32770)
    # P < (8/3)^11 < e^11; log(4*P^(k/2)+1)<log(8*P^(k/2)).
    assert P * 3 ** 11 < 8 ** 11
    denominator_upper = 3 + (K_EXPONENT // 2) * 11
    assert K_EXPONENT % 2 == 0 and denominator_upper == 90115
    delta_lower = numerator_lower / denominator_upper
    assert delta_lower > Q(1, 1000000)
    return delta_lower


def finite_target(root):
    data = json.loads((root / 'certificates/residue11_coloring.json').read_text())
    assert data['field_order'] == 11 and data['colors'] == 5
    rows = data['rows']
    assert len(rows) == 11 and all(len(row) == 11 for row in rows)
    colors = [int(c) for row in rows for c in row]
    assert set(colors) == set(range(5))
    points = list(product(range(11), repeat=2))
    assert all(x == y == 0 for x, y in points if (x * x + y * y) % 11 == 0)
    edges = [(a, b) for a, b in combinations(range(121), 2)
             if sum((x - y) ** 2 for x, y in zip(points[a], points[b])) % 11 == 1]
    assert len(edges) == 726
    assert all(colors[a] != colors[b] for a, b in edges)
    return len(edges)


def verify(root=None):
    if not __debug__:
        raise RuntimeError('Do not disable assertions in a mathematical checker.')
    root = root or Path(__file__).resolve().parents[1]
    discriminant_factor, roots11, lifts = local_parameters()
    delta_lower = exponent_bound(discriminant_factor)
    edges = finite_target(root)
    return dict(theorem='T083', status='LOCAL_PARAMETERS_AND_EXPONENT_VERIFIED',
                radicands=list(T), auxiliary_split_prime=P, D=discriminant_factor,
                roots_mod11=roots11, hensel_calibrations=lifts,
                prescribed_split_places=5, real_split_places=2,
                gs_generators_at_least=7, gs_relation_excess_at_most=5,
                residue_vertices=121, residue_edges=edges,
                density_exponent_increment='1/1000000',
                strict_delta_lower_bound=str(delta_lower),
                scope='Infinite tower and density existence use the external '
                      'inputs and written proof; this is not a tower certificate.')


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
