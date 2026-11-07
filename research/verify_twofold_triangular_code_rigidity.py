#!/usr/bin/env python3
"""Exact binary 2-fold 1-ball code rigidity for the infinite triangular grid.

Uses only integer combinatorics and exhaustive branching. No SAT solver,
floating-point arithmetic, heuristic sampling, or unverified optimum claims.
The global conclusion also needs the elementary overlap argument in the report.
"""
from itertools import combinations
import json

R=4
DELTAS=((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1))
VERTS=[(m,n) for m in range(-R,R+1) for n in range(-R,R+1)]
INDEX={v:i for i,v in enumerate(VERTS)}
EQS=[tuple(INDEX[m+a,n+b] for a,b in DELTAS)
     for m in range(1-R,R) for n in range(1-R,R)]
PATCH=[(m,n) for m in range(-2,3) for n in range(-2,3)]
PATCH_INDICES=[INDEX[p] for p in PATCH]


def require(ok,msg):
    if not ok:
        raise RuntimeError(msg)


def templates():
    result=[]
    for slope in (3,5):
        for a,b in combinations(range(7),2):
            pattern=tuple(int((m+slope*n)%7 in (a,b)) for m,n in PATCH)
            result.append((slope,a,b,pattern))
    require(len(result)==42 and len({t[-1] for t in result})==42,
            'the two chiralities have 42 distinct central code patterns')
    for slope,a,b,_ in result:
        for m in range(7):
            for n in range(7):
                require(sum(int((m+x+slope*(n+y))%7 in (a,b))
                            for x,y in DELTAS)==2,
                        'each proposed template is an exact twofold cover')
    return result


def propagate(vals):
    changed=True
    while changed:
        changed=False
        for row in EQS:
            n1=0
            unknown=[]
            for j in row:
                if vals[j]==1:
                    n1+=1
                elif vals[j]==-1:
                    unknown.append(j)
            remaining=2-n1
            if remaining<0 or remaining>len(unknown):
                return False
            if unknown and (remaining==0 or remaining==len(unknown)):
                forced=int(remaining!=0)
                for j in unknown:
                    vals[j]=forced
                    changed=True
    return True


def enumerate_exact_center_patterns(expected):
    stats={'nodes':0,'completed_partial_assignments':0}
    seen=set()

    def dfs(vals):
        stats['nodes']+=1
        if not propagate(vals):
            return
        best=None
        nchoices=1000000
        for row in EQS:
            ones=sum(vals[j]==1 for j in row)
            unknown=tuple(j for j in row if vals[j]==-1)
            if not unknown:
                continue
            remaining=2-ones
            choices=len(tuple(combinations(unknown,remaining)))
            if 1<choices<nchoices:
                best=(unknown,remaining)
                nchoices=choices
        if best is None:
            stats['completed_partial_assignments']+=1
            require(all(vals[j] in (0,1) for j in PATCH_INDICES),
                    'central 25 sites are fully determined at all leaves')
            p=tuple(vals[j] for j in PATCH_INDICES)
            require(p in expected,'non-code center pattern found')
            seen.add(p)
            return
        unknown,remaining=best
        for chosen in combinations(unknown,remaining):
            chosen=set(chosen)
            branch=vals[:]
            for j in unknown:
                branch[j]=int(j in chosen)
            dfs(branch)

    dfs([-1]*len(VERTS))
    require(len(seen)==42,'each template occurs in a feasible local patch')
    stats.update({'central_patterns_reached':len(seen),
                  'non_code_patterns_found':0})
    return stats


def verify_overlap_uniqueness(codes):
    # Neighboring 5x5 windows overlap in 20 cells. The exact integer
    # comparison is between full-plane templates, not translated labels.
    for sx,sy in ((1,0),(0,1)):
        overlap=sorted(set(PATCH).intersection(
            {(m+sx,n+sy) for m,n in PATCH}))
        require(len(overlap)==20,'twenty-site overlap for two generators')
        for i,(slope,a,b,_) in enumerate(codes):
            for j,(slope2,a2,b2,_) in enumerate(codes):
                if i==j:
                    continue
                if all(int((m+slope*n)%7 in (a,b))==
                       int((m+slope2*n)%7 in (a2,b2))
                       for m,n in overlap):
                    raise RuntimeError('two distinct templates agree on overlap')
    return {'generators':[[1,0],[0,1]],
            'overlap_sites_per_generator':20,
            'pairs_of_distinct_templates_that_agree':0}


def main():
    require(len(VERTS)==81 and len(EQS)==49 and len(PATCH)==25,
            '9x9 binary window, 49 star equations, central 5x5 patch')
    codes=templates()
    return {'status':'PASS',
            'proof_scope':'exact exhaustive local enumeration and overlap uniqueness',
            'finite_window_vertices':81,
            'finite_star_equations':49,
            'central_patch_vertices':25,
            'templates':len(codes),
            'enumeration':enumerate_exact_center_patterns({t[-1] for t in codes}),
            'overlap_uniqueness':verify_overlap_uniqueness(codes),
            'global_classification':
                'every exact twofold radius-one triangular-grid cover is the union of two cosets of m+3n or m+5n modulo 7',
            'hn_scope':'only exact 2/7 saturation; no unconditional chi=7 proof'}


if __name__=='__main__':
    print(json.dumps(main(),sort_keys=True,indent=2))
