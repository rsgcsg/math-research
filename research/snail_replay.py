"""Independent exact replay of the external G29 geometric fractional dual.

Uses manuscript coordinates, verified congruence rows and integer subset-zeta
summation. Does not execute supplied scripts, unpickle verts_sym.npy, or trust
the supplied IEC matrix. Only Python's standard library is needed.
"""
import argparse
import ast
import hashlib
import json
import math
import re
import struct
import zipfile
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from snail_geometry import geometry


def independent_sets(n,edges):
    neighbors=[0]*n
    for a,b in edges:
        neighbors[a]|=1<<b
        neighbors[b]|=1<<a
    atoms=[0]
    for v in range(n):
        atoms += [mask | (1<<v) for mask in atoms if not mask & neighbors[v]]
    return atoms


def run(archive,progress=True):
    def report(message):
        if progress:
            print(message,flush=True)
    sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as z:
        def read(name):
            return z.read('snail_reproduction/'+name)
        congs_text=read('congruences.txt').decode()
        dual_text=read('rational_dual.txt').decode()
        adj_raw=read('true_adj.npy')
    report('Building all 406 exact pair distances from manuscript radicals')
    pts,distances,edges=geometry()
    assert len(edges)==51
    assert [(a,b) for a,b in edges if a<2]==[(0,4),(1,4)]
    # Compare the archive adjacency only after independent exact construction.
    assert adj_raw[:8]==b'\x93NUMPY\x01\x00'
    hlen=struct.unpack('<H',adj_raw[8:10])[0]
    header=ast.literal_eval(adj_raw[10:10+hlen].decode().strip())
    assert header=={'descr':'|b1','fortran_order':False,'shape':(29,29)}
    raw=adj_raw[10+hlen:]
    assert len(raw)==29*29
    edge_set=set(edges)
    assert all(raw[29*i+j]==int(tuple(sorted((i,j))) in edge_set) for i in range(29) for j in range(29))
    atoms=independent_sets(29,edges)
    assert len(atoms)==len(set(atoms))==498168
    atom_set=set(atoms)
    report(f'Exact geometry PASS: {len(edges)} induced edges; {len(atoms)} independent sets')
    congs=[]
    pair_checks=set()
    pattern=re.compile(r'^\S+\s+(\[.*?\])\s*=\s*(\[.*?\])$')
    for line in congs_text.splitlines():
        match=pattern.fullmatch(line.strip())
        assert match, 'Unparsed congruence line'
        left,right=[ast.literal_eval(match.group(i)) for i in (1,2)]
        assert len(left)==len(right)>0
        assert len(set(left))==len(left) and len(set(right))==len(right)
        assert all(type(x)==int and 0<=x<29 for x in left+right)
        for i,j in combinations(range(len(left)),2):
            a=tuple(sorted((left[i],left[j])))
            b=tuple(sorted((right[i],right[j])))
            assert distances[a]==distances[b]
            pair_checks.add((a,b))
        lm=sum(1<<v for v in left)
        rm=sum(1<<v for v in right)
        assert lm in atom_set and rm in atom_set
        congs.append((lm,rm))
    dual=[]
    for line in dual_text.splitlines():
        if line.strip() and not line.startswith('#'):
            n,d=map(int,line.split())
            assert d>0
            dual.append((n,d))
    assert len(dual)==len(congs)
    denominator=math.lcm(*(d for n,d in dual))
    numerator=4000716307
    assert denominator==1000000018
    report(f'All {len(congs)} congruences verified; aggregating rational dual')
    h=defaultdict(int)
    for (left,right),(n,d) in zip(congs,dual):
        weight=n*(denominator//d)
        h[left]+=weight
        h[right]-=weight
    values={mask:h.get(mask,0) for mask in atoms}
    # Zeta transform on this down-closed family: every I\{v} is an atom too.
    for v in range(29):
        bit=1<<v
        for mask in atoms:
            if mask&bit:
                values[mask]+=values[mask^bit]
    slacks=[values[mask]-numerator*int(bool(mask&1))+denominator for mask in atoms]
    assert min(slacks)>=0
    assert F(numerator,denominator)>F(40007,10000)
    report(f'All {len(slacks)} integer dual inequalities PASS; min slack {min(slacks)}')
    return dict(status='VERIFIED_EXTERNAL_GFCN_LOWER_BOUND',archive_sha256=sha,
                source='https://users.renyi.hu/~akos/ep1070/data/snail.zip',
                vertices=29,induced_edges=len(edges),all_pairs_checked=len(distances),
                independent_sets=len(atoms),congruences=len(congs),
                distinct_congruence_pair_checks=len(pair_checks),dual_inequalities=len(slacks),
                dual_numerator=numerator,dual_denominator=denominator,
                minimum_integer_slack=min(slacks),zero_slack_atoms=slacks.count(0),
                bound=str(F(numerator,denominator)),ordinary_graph_chromatic_claim='not inferred',
                author_scripts_executed=False,pickled_vertex_array_loaded=False,
                cached_iec_matrix_used=False)


if __name__=='__main__':
    import sys
    if not __debug__:
        sys.exit('Do not disable assertions in an exact verifier.')
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path,default=Path('references/cache/snail.zip'))
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=run(args.archive)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
