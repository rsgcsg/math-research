"""Exact original G27 dual replay, independent of its cached sparse matrix."""
import argparse
import hashlib
import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from snail_geometry import geometry, vertices, scalar, radical, cmul, cadd, scale
from snail_replay import independent_sets


def replay(cache):
    paths={name:cache/f'g27_{name}.txt' for name in ('coeffs','isometries','witness')}
    hashes={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in paths.items()}
    one=(scalar(1),scalar())
    from fractions import Fraction as F
    w=(scalar(F(1,2)),tuple(x/2 for x in radical(1)))
    rho=(scalar(F(5,6)),tuple(x/6 for x in radical(2)))
    basis=(one,w,rho,cmul(w,rho))
    coeffs=[list(map(int,line.split())) for line in paths['coeffs'].read_text().splitlines()]
    assert len(coeffs)==27 and all(len(row)==4 for row in coeffs)
    assert [cadd(*(scale(b,c) for b,c in zip(basis,row))) for row in coeffs]==vertices()[2:]
    _,d,all_edges=geometry()
    edges=[(a-2,b-2) for a,b in all_edges if a>=2]
    atoms=independent_sets(27,edges)
    assert len(atoms)==182304
    atom_set=set(atoms)
    congs=[]
    for line in paths['isometries'].read_text().splitlines():
        row=list(map(int,line.split()))
        assert len(row)==27 and all(-1<=v<27 for v in row)
        left=[i for i,v in enumerate(row) if v>=0]
        right=[row[i] for i in left]
        assert left and len(right)==len(set(right))
        for a,b in combinations(left,2):
            assert d[a+2,b+2]==d[tuple(sorted((row[a]+2,row[b]+2)))]
        masks=[sum(1<<i for i in side) for side in (left,right)]
        assert all(m in atom_set for m in masks)
        congs.append(masks)
    dual=[tuple(map(int,line.split())) for line in paths['witness'].read_text().splitlines()]
    assert len(dual)==len(congs)==16855
    assert all(len(row)==2 and row[1]>0 for row in dual)
    denominator=math.lcm(*(den for num,den in dual))
    h=defaultdict(int)
    for (left,right),(num,den) in zip(congs,dual):
        weight=num*(denominator//den)
        h[left]+=weight
        h[right]-=weight
    values={mask:h.get(mask,0) for mask in atoms}
    for v in range(27):
        bit=1<<v
        for mask in atoms:
            if mask&bit:
                values[mask]+=values[mask^bit]
    slacks={mask:values[mask]+denominator-4*denominator*int(bool(mask&1)) for mask in atoms}
    assert min(slacks.values())>=0
    tight=sorted(mask for mask in atoms if slacks[mask]==0)
    result=dict(status='VERIFIED_EXTERNAL_G27_DUAL',sources_sha256=hashes,
                vertices=27,induced_edges=len(edges),independent_sets=len(atoms),
                congruences=len(congs),dual_inequalities=len(slacks),
                denominator=str(denominator),minimum_integer_slack=min(slacks.values()),
                zero_slack_atoms=len(tight),tight_masks=tight,
                bound='4',support_exhaustion_claim='every feasible total-mass-4 geometric fractional law is supported in tight_masks')
    return result


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Do not disable assertions in an exact verifier.')
    parser=argparse.ArgumentParser()
    parser.add_argument('--cache',type=Path,default=Path('references/cache'))
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=replay(args.cache)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='tight_masks'},indent=2))
