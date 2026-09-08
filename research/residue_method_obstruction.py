"""Export the finite arithmetic part of T053/T054; no spectral numerical test."""
import json
from math import isqrt
from pathlib import Path


def run():
    primes = [p for p in range(3, 98) if all(p % j for j in range(2, isqrt(p)+1))]
    rows = []
    for p in primes:
        q, exponent = p, 1
        while q <= 97:
            if q % 4 == 3:
                blockers = [d for d in (3, 5, 11) if pow(d % p, (p-1)//2, p) == p-1]
                rows.append(dict(q=q, p=p, exponent=exponent,
                                 base_blocker=blockers[0] if blockers else None))
            q *= p
            exponent += 1
    rows.sort(key=lambda row: row['q'])
    conics = []
    for p in (131, 491):
        roots = {str(d): next(x for x in range(p) if x*x % p == d)
                 for d in (3, 5, 11, 13)}
        conics.append(dict(p=p, roots=roots,
                           homogeneous_parameters=[[1, t] for t in range(p)]+[[0, 1]]))
    return dict(schema=1, spectral_cutoff=97, small_anisotropic_orders=rows,
                escape_nonsquares_mod11=[7, 13, 17, 41], conics=conics,
                scope='Finite arithmetic and edge-lift calibration only; Weil bound and CRT theorem are written dependencies')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    data = run()
    (root/'certificates/residue_method_obstruction.json').write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(dict(small_orders=len(data['small_anisotropic_orders']),
                         conic_parameters=sum(len(c['homogeneous_parameters']) for c in data['conics']))))
