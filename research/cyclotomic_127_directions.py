"""Construct the T077 denominator-127 direction certificate (exact rationals).

The proof gives completeness; verify_cyclotomic_127.py independently checks
the integer identities and all listed directions without importing this file.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import json


def mul(a, b):
    c = [Fraction(0)]*11
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i+j] += x*y
    for i in range(10, 5, -1):
        for j in range(6):
            c[i-6+j] -= c[i]
    return tuple(c[:6])


def root(j):
    j %= 7
    return tuple(Fraction(-1 if j == 6 else int(i == j)) for i in range(6))


def build():
    one = root(0)
    factors = [tuple(2*x-y for x, y in zip(one, root(j))) for j in range(1, 7)]
    ratios = []
    for j in range(1, 4):
        # 1/(2-z^j) = product of the other five factors / 127.
        inv = one
        for k in range(1, 7):
            if k != j:
                inv = mul(inv, factors[k-1])
        ratios.append(mul(factors[6-j], tuple(x/127 for x in inv)))
    records = []
    for exponents in product((-1, 0, 1), repeat=3):
        value = one
        for j, e in enumerate(exponents):
            ratio = ratios[j]
            if e == -1:
                ratio = tuple(sum(ratio[k]*root(-k)[i] for k in range(6)) for i in range(6))
            if e:
                value = mul(value, ratio)
        for k in range(7):
            for sign in (-1, 1):
                numerator = tuple(sign*127*x for x in mul(value, root(k)))
                assert all(x.denominator == 1 for x in numerator)
                records.append(dict(exponents=list(exponents), root_power=k, sign=sign,
                                    numerator=[int(x) for x in numerator]))
    return dict(schema=1, theorem='T077', denominator=127,
                basis='1,z,z^2,z^3,z^4,z^5; Phi_7(z)=0',
                convention='r_j=(2-z^(-j))/(2-z^j), j=1,2,3',
                directions=records)


if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1]/'certificates/cyclotomic_127_directions.json'
    data = build()
    path.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(dict(output=str(path), directions=len(data['directions']))))
