"""G27 joint-distribution search and exact rational witness extraction.

The 168-atom support is taken from the external optimal-face list and compared
with the original dual's independently checked tight set when available.
It is exhaustive for invariant mass-four laws, NOT for arbitrary G27 colorings.
Positive witnesses are independently checked by verify_joint_face.py.
"""
import ast
import json
import re
import zipfile
from itertools import combinations,permutations
from pathlib import Path
from fractions import Fraction as F
from snail_geometry import geometry
from snail_replay import independent_sets
from joint_isometries import maximal_maps, pattern


def run(archive,full=False,classify=False):
    import numpy as np
    from scipy.optimize import linprog
    pts,dist,edges=geometry()
    base_edges=[(a-2,b-2) for a,b in edges if a>=2]
    atoms=independent_sets(27,base_edges)
    assert len(atoms)==182304
    with zipfile.ZipFile(archive) as z:
        face=json.loads(z.read('snail_reproduction/optimal_face_vertices.json'))
        text=z.read('snail_reproduction/congruences.txt').decode()
    support=sorted({atoms[int(i)] for v in face for i in v['support']})
    assert len(support)==168
    dual_path=Path('certificates/g27_replay.json')
    dual=json.loads(dual_path.read_text()) if dual_path.exists() else None
    if dual is not None:
        assert support==dual['tight_masks']
    by_vertex=[[s for s in support if s>>v&1] for v in range(27)]
    covers=[]
    def visit(left,parts):
        if not left:
            if len(parts)<=4:
                covers.append(parts)
            return
        if len(parts)>=4:
            return
        v=(left&-left).bit_length()-1
        for s in by_vertex[v]:
            if s&left==s:
                visit(left^s,parts+[s])
    visit((1<<27)-1,[])
    assert len(covers)==348 and all(len(p)==4 for p in covers)
    colorings=np.empty((len(covers),27),dtype=np.int8)
    for i,p in enumerate(covers):
        for label,s in enumerate(p):
            for v in range(27):
                if s>>v&1:
                    colorings[i,v]=label
    congruences=[]
    for line in text.splitlines():
        match=re.fullmatch(r'^\S+\s+(\[.*?\])\s*=\s*(\[.*?\])$',line)
        assert match
        left,right=[ast.literal_eval(match.group(i)) for i in (1,2)]
        if any(v<2 for v in left+right):
            continue
        congruences.append((tuple(v-2 for v in left),tuple(v-2 for v in right)))
    cache={}
    def mono(vs):
        if vs not in cache:
            cache[vs]=np.all(colorings[:,vs]==colorings[:,vs[0],None],axis=1).astype(np.int8)
        return cache[vs]
    rows={}
    for left,right in congruences:
        row=mono(left)-mono(right)
        if np.any(row):
            rows[row.tobytes()]=row
    matrix=np.array(list(rows.values()),dtype=np.int8)
    deterministic=np.flatnonzero(np.all(matrix==0,axis=0))
    target=np.ones(len(covers));target[deterministic]=0
    results=[]
    witnesses=[]
    def solve(stage):
        mat=np.array(list(rows.values()),dtype=np.int8)
        A=np.vstack([np.ones(len(covers),dtype=np.int8),mat])
        rhs=np.zeros(len(A));rhs[0]=1
        result=linprog(-target,A_eq=A,b_eq=rhs,bounds=(0,None),method='highs')
        assert result.success,result.message
        weights=[F(float(x)).limit_denominator(10**6) if x>1e-9 else F(0) for x in result.x]
        assert sum(weights)==1 and all(w>=0 for w in weights)
        assert all(sum(int(v)*w for v,w in zip(row,weights))==0 for row in mat)
        witnesses.append([dict(blocks=covers[i],weight=str(w)) for i,w in enumerate(weights) if w])
        results.append(dict(stage=stage,rows=len(mat),columns=len(covers),
                            individually_geometric_columns=len(deterministic),
                            max_nongeometric_mass=-result.fun,
                            positive_columns=int(np.count_nonzero(result.x>1e-9)),
                            rational_weights_verified=True))
        print(json.dumps(results[-1]),flush=True)
    solve('all_supplied_monochromatic_congruences')
    # All four-point congruences, including automorphisms; three disjoint-pair
    # events are exactly the additional partition observables at four points.
    ids={}
    distances={}
    for i,j in combinations(range(27),2):
        d=dist[i+2,j+2]
        distances[i,j]=distances[j,i]=ids.setdefault(d,len(ids))
    references={}
    pairings=[((0,1),(2,3)),((0,2),(1,3)),((0,3),(1,2))]
    for subset in combinations(range(27),4):
        candidates=[]
        for order in permutations(subset):
            key=tuple(distances[order[i],order[j]] for i,j in combinations(range(4),2))
            candidates.append((key,order))
        best=min(key for key,order in candidates)
        for key,order in candidates:
            if key!=best:
                continue
            for pairing_idx,((a,b),(c,d)) in enumerate(pairings):
                values=((colorings[:,order[a]]==colorings[:,order[b]]) &
                        (colorings[:,order[c]]==colorings[:,order[d]])).astype(np.int8)
                refkey=(best,pairing_idx)
                if refkey not in references:
                    references[refkey]=values
                else:
                    row=values-references[refkey]
                    if np.any(row):
                        rows[row.tobytes()]=row
    solve('plus_all_quartet_2plus2_congruences')
    if full:
        maps=maximal_maps(pts[2:],{(a-2,b-2):d for (a,b),d in dist.items() if a>=2})
        print(f'Full partial isometries: {len(maps)}',flush=True)
        for mapping in maps:
            left,right=zip(*mapping)
            patterns_left=[pattern(c,left) for c in colorings]
            patterns_right=[pattern(c,right) for c in colorings]
            for p in set(patterns_left+patterns_right):
                row=np.array([int(a==p)-int(b==p) for a,b in zip(patterns_left,patterns_right)],dtype=np.int8)
                if np.any(row):
                    rows[row.tobytes()]=row
        solve('all_partial_isometry_full_partition_laws')
        if classify:
            from scipy.linalg import qr
            from sympy import Matrix
            mat=np.array(list(rows.values()),dtype=np.int8)
            _,r,pivots=qr(mat.T.astype(float),mode='economic',pivoting=True)
            rank=int(np.count_nonzero(np.abs(np.diag(r))>1e-7))
            print(f'Numerical homogeneous rank {rank}; checking selected rows exactly',flush=True)
            reduced,piv=Matrix(mat[pivots[:rank],:].tolist()).rref()
            assert len(piv)==rank
            free=[i for i in range(len(covers)) if i not in piv]
            null=Matrix.zeros(len(covers),len(free))
            for j,c in enumerate(free):
                null[c,j]=1
                for i,p in enumerate(piv):
                    null[p,j]=-reduced[i,c]
            # RREF is only of selected rows: check the resulting kernel against
            # ALL equations exactly, not just the numerical rank estimate.
            from math import lcm
            denominator=lcm(*(int(x.q) for x in null))
            int_null=np.array((denominator*null).tolist(),dtype=np.int64)
            assert int(np.max(np.abs(int_null)))*len(covers)<2**63
            assert not np.any(mat.astype(np.int64)@int_null)
            active=[i for i in range(len(covers)) if any(null[i,j] for j in range(len(free)))]
            kernel=dict(rank=rank,nullity=len(free),linearly_allowed_columns=len(active),
                        free_columns=free,active_columns=active,
                        covers=[covers[i] for i in active],
                        kernel_rows=[[str(null[i,j]) for j in range(len(free))] for i in active])
            print(json.dumps({k:kernel[k] for k in ('rank','nullity','linearly_allowed_columns')}),flush=True)
            # Strictly positive law decides whether any of the 348 columns can
            # be ruled out even after all full-partition congruence equations.
            K=int_null.astype(float)/denominator
            interior=linprog([0]*len(free)+[-1],
                             A_ub=np.column_stack([-K,np.ones(len(covers))]),
                             b_ub=np.zeros(len(covers)),
                             A_eq=[list(K.sum(axis=0))+[0]],b_eq=[1],
                             bounds=(0,None),method='highs')
            assert interior.success and interior.x[-1]>0
            z=[F(float(x)).limit_denominator(10**6) for x in interior.x[:-1]]
            p=[sum(F(str(null[i,j]))*z[j] for j in range(len(free))) for i in range(len(covers))]
            assert min(p)>0 and sum(p)==1
            kernel['interior_witness']=[dict(blocks=c,weight=str(w)) for c,w in zip(covers,p)]
            kernel['minimum_probability']=str(min(p))
            print(f'Exact strictly positive law: all {len(p)} columns; min {min(p)}',flush=True)
    return dict(status='EXACT_POSITIVE_WEIGHTS_SEARCH_GENERATED',support_atoms=len(support),
                candidate_partitions=len(covers),results=results,
                witnesses=witnesses,support_matches_original_dual_tight_atoms=dual is not None,
                negative_claims_certified=False,
                exact_kernel=kernel if full and classify else None)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path,default=Path('references/cache/snail.zip'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--full',action='store_true')
    parser.add_argument('--classify',action='store_true')
    args=parser.parse_args()
    if args.classify and not args.full:
        parser.error('--classify requires --full')
    result=run(args.archive,args.full,args.classify)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
