"""Compile the complete H=<eta,u> unit-contact voltage graph (T125).

Search-side numpy sieve; all survivors use exact integer algebra. Independent
verification lives elsewhere. A finite voltage table is not a coloring.
"""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import math
import time

import numpy as np

from rotation_orbit_equalities import rotations, integer_action
from verify_quintic_core_probe import (RAD, conjugate_twice, digest,
                                      product_twice)
from verify_quintic_tau_union import verify as source_geometry


def split_map(table, start):
    for prime in range(start, start + 100000):
        if prime % 20 != 1 or any(prime % d == 0 for d in range(2, math.isqrt(prime)+1)):
            continue
        if all(pow(r, (prime-1)//2, prime) == 1 for r in (3, 11)):
            break
    else:
        raise AssertionError('No split prime')
    eta = next(pow(x, (prime-1)//5, prime) for x in range(2, prime)
               if pow(x, (prime-1)//5, prime) != 1)
    roots = {r: next(x for x in range(1, prime) if x*x % prime == r % prime)
             for r in (3, 11, -1)}
    roots[5] = (2*(eta+pow(eta, -1, prime))+1) % prime
    images = []
    for e in range(2):
        for imaginary in range(2):
            for rad in RAD:
                value = (eta if e else 1)*(roots[-1] if imaginary else 1)
                for r in (3, 5, 11):
                    if rad % r == 0:
                        value *= roots[r]
                images.append(value % prime)
    assert all(sum(c*images[k] for k, c in row) % prime == 2*images[i]*images[j] % prime
               for (i,j), row in table.items())
    bars = [sum(x*y for x,y in zip(conjugate_twice([int(i == j) for j in range(32)]), images))
            *pow(2,-1,prime) % prime for i in range(32)]
    return prime, images, bars


def canonical(i, j, h, n):
    h %= 5
    if n < 0 or (n == 0 and h > 2) or (n == h == 0 and i > j):
        return (j, i, (-h) % 5, -n)
    return (i, j, h, n)


def build(root, progress=True):
    assert __debug__, 'Do not use -O'
    root = Path(root)
    started = time.monotonic()
    _, ctx = source_geometry(root, geometry_context=True)
    table = ctx['ring']['table']
    eqpath = root/'certificates/rotation_orbit_equalities.json'
    eq = json.loads(eqpath.read_text())
    den = math.lcm(*(x.denominator for p in ctx['points'] for x in p))
    allpoints = [tuple(int(x*den) for x in p) for p in ctx['points']]
    assert digest(allpoints) == eq['source_point_sha256']
    reps = eq['representatives']
    points = [allpoints[i] for i in reps]
    assert len(points) == 4176 and den == 480
    maps = [split_map(table, start) for start in (4001, 10001)]
    projected = []
    for prime, images, bars in maps:
        invden = pow(den, -1, prime)
        projected.append((np.array([sum(x*y for x,y in zip(p,images))*invden % prime for p in points], dtype=np.int64),
                          np.array([sum(x*y for x,y in zip(p,bars))*invden % prime for p in points], dtype=np.int64)))
    contacts, stats = [], []
    for h, n, rotation in rotations(table, 9):
        if n < 0 or (n == 0 and h > 2):
            continue
        rows, action_den = integer_action(rotation, table)
        transforms = {}
        factors = []
        for prime, images, bars in maps:
            ev = lambda basis: sum(int(x.numerator)*pow(x.denominator,-1,prime)*y
                                   for x,y in zip(rotation,basis)) % prime
            factors.append((ev(images), ev(bars)))
            assert factors[-1][0]*factors[-1][1] % prime == 1
        prime = maps[0][0]
        a, abar = projected[0]
        b = a*factors[0][0] % prime
        bbar = abar*factors[0][1] % prime
        prime2 = maps[1][0]
        a2, abar2 = projected[1]
        b2 = a2*factors[1][0] % prime2
        bbar2 = abar2*factors[1][1] % prime2
        first = second = count = 0
        norm_target = [4*(den*action_den)**2] + [0]*31
        for begin in range(0,len(points),128):
            end = min(begin+128,len(points))
            sieve = ((a[begin:end,None]-b[None,:])*(abar[begin:end,None]-bbar[None,:])-1) % prime == 0
            ii,jj = np.nonzero(sieve)
            ii += begin
            if h == n == 0:
                keep = ii < jj
                ii,jj = ii[keep],jj[keep]
            first += len(ii)
            keep = ((a2[ii]-b2[jj])*(abar2[ii]-bbar2[jj])-1) % prime2 == 0
            ii,jj = ii[keep],jj[keep]
            second += len(ii)
            for i,j in zip(ii.tolist(),jj.tolist()):
                if j not in transforms:
                    transforms[j] = tuple(sum(points[j][k]*c for k,c in row) for row in rows)
                delta = [x*action_den-y for x,y in zip(points[i],transforms[j])]
                if product_twice(delta,conjugate_twice(delta),table) == norm_target:
                    contacts.append([i,j,h,n])
                    count += 1
        stats.append(dict(h=h,n=n,first_survivors=first,second_survivors=second,contacts=count))
        if progress:
            print(json.dumps(dict(stage='contacts',elapsed=round(time.monotonic()-started,2),**stats[-1])),flush=True)
    contacts.sort()
    assert len(set(map(tuple, contacts))) == len(contacts)
    # Full ordered gain table has at most two gains per representative pair.
    full = set()
    for i,j,h,n in contacts:
        full.add((i,j,h,n))
        full.add((j,i,(-h)%5,-n))
    paircounts = Counter((i,j) for i,j,h,n in full)
    assert max(paircounts.values()) <= 2
    origin = [i for i,p in enumerate(points)
              if product_twice(p,conjugate_twice(p),table) == [4*den*den]+[0]*31]
    # Every actual source edge must have its H-normalized edge in the table.
    repindex = {r:i for i,r in enumerate(reps)}
    edgeset = set(map(tuple,contacts))
    zero = eq['zero_indices'][0]
    for a,b in ctx['edges']:
        if zero in (a,b):
            v = b if a == zero else a
            assert repindex[eq['coordinates'][v][0]] in origin
            continue
        ri,hi,ni = eq['coordinates'][a]
        rj,hj,nj = eq['coordinates'][b]
        assert canonical(repindex[ri],repindex[rj],hj-hi,nj-ni) in edgeset
    return dict(schema=1,kind='complete_rotation_orbit_unit_contacts',
                equality_sha256=hashlib.sha256(eqpath.read_bytes()).hexdigest(),
                source_sha256=eq['source_sha256'],source_point_sha256=eq['source_point_sha256'],
                representatives=reps,representative_count=len(reps),
                convention='|r_i - eta^h u^n r_j| = 1; inverse edges identified',
                completeness=dict(theorem='T125 section 9',absolute_offset_bound=9,
                                  canonical_rule='n>0; or n=0,h=1,2; or n=h=0,i<j'),
                contacts=contacts,contact_count=len(contacts),contact_sha256=digest(contacts),
                origin_neighbors=origin,origin_neighbor_count=len(origin),
                ordered_pair_gain_histogram=sorted(Counter(paircounts.values()).items()),
                modular_filter_primes=[m[0] for m in maps],scan=stats,
                scope='Complete actual induced H-orbit graph, pending independent replay; no coloring or NON5 asserted.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    print('ROTATION_CONTACTS_JSON='+json.dumps(build(Path(__file__).resolve().parents[1],not args.quiet),separators=(',',':')),flush=True)
