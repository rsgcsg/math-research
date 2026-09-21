"""E101 producer: integral cycle witnesses for nilpotent support covers.

Search-side dependencies: NumPy and SymPy. The checker imports neither this
module nor those libraries. No SAT result is used as a proof certificate.
"""
from collections import deque
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from sympy import Matrix
from dyadic_mixed_return_joint import prepare


def reduce_word(word):
    out = []
    for x in word:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return out


def build(root):
    report, context, source, _, _, definitions, mappings = prepare(root)
    old = source['result']; n = len(context['points']); count = 25*n
    adjacency = [[] for _ in range(count)]; edges = []
    for j, mapping in enumerate(mappings[:14]):
        for a in range(5):
            b = old['word_permutations'][j][a]
            pi = old['color_permutations'][j][a]; label = 5*j+a
            for x, y in mapping:
                for c in range(5):
                    u = (a*n+x)*5+c; v = (b*n+y)*5+pi[c]
                    adjacency[u].append((v, label+1))
                    adjacency[v].append((u, -label-1)); edges.append((u,v,label))
    seeds = [155, 156, 159]  # (word 0, point 31, colors 0,1,4)
    parent = {}; parent_step = {}; component = {}
    potentials = np.zeros((count,70),dtype=np.int16)
    for part, seed in enumerate(seeds):
        parent[seed] = None; component[seed] = part; queue = deque([seed])
        while queue:
            u = queue.popleft()
            for v, step in adjacency[u]:
                if v in parent:
                    assert component[v] == part
                    continue
                parent[v] = u; parent_step[v] = step; component[v] = part
                potentials[v] = potentials[u]
                potentials[v,abs(step)-1] += 1 if step>0 else -1
                queue.append(v)
    del adjacency
    cycle_rows = [{} for _ in seeds]
    for u,v,label in edges:
        if u not in component:
            continue
        row = potentials[u]-potentials[v]; row[label] += 1
        if not np.any(row):
            continue
        values = tuple(map(int,row)); orientation = 1
        if next(x for x in values if x) < 0:
            values = tuple(-x for x in values); orientation = -1
        cycle_rows[component[u]].setdefault(values,(u,v,label,orientation))
    tree = [10,11,12,13]
    chords = [j for j in range(70) if j not in tree]
    def path(v):
        steps = []
        while parent[v] is not None:
            steps.append(parent_step[v]); v = parent[v]
        return list(reversed(steps))
    parts = []
    for k, rows in enumerate(cycle_rows):
        row_list = list(rows); matrix = np.array(row_list,dtype=np.int64)[:,chords]
        selected_cycles = []; cycle_ids = {}; minors = []; common = 0
        for prime in [2,3,5,37,7,11]:
            basis = {}; selected = []
            for i, row in enumerate(matrix):
                v = row.copy()%prime
                for pivot, reduced in basis.items():
                    if v[pivot]:
                        v = (v-v[pivot]*reduced)%prime
                nz = np.flatnonzero(v)
                if len(nz):
                    pivot = int(nz[0]); basis[pivot] = v*pow(int(v[pivot]),-1,prime)%prime
                    selected.append(i)
                if len(selected)==66:
                    break
            assert len(selected)==66
            determinant = int(Matrix(matrix[selected].tolist()).det(method='domain-ge'))
            ids = []
            for i in selected:
                if i not in cycle_ids:
                    u,v,label,sign = rows[row_list[i]]
                    word = path(u)+[label+1]+[-x for x in reversed(path(v))]
                    if sign < 0:
                        word = [-x for x in reversed(word)]
                    cycle_ids[i] = len(selected_cycles)
                    selected_cycles.append(reduce_word(word))
                ids.append(cycle_ids[i])
            minors.append(dict(cycles=ids,determinant=determinant))
            common = math.gcd(common,determinant)
            if common==1:
                break
        assert common==1
        parts.append(dict(seed=seeds[k],cycles=selected_cycles,minors=minors))
    required = {(a*n+p)*5+c for a in range(5)
                for p in [233,239,5557,238] for c in range(5)}
    required.update((0*n+31)*5+c for c in range(5))
    required.add((0*n+193)*5+4)
    transports = [dict(node=v,component=component[v],path=path(v)) for v in sorted(required)]
    return dict(schema='joint-nilpotent-cover-v1',experiment='E101',
                source_sha256=hashlib.sha256((root/'certificates/quintic_multiword_return_joint.json').read_bytes()).hexdigest(),
                geometry=report['geometry'],base_vertices=5,base_edges=70,
                tree_edges=tree,parts=parts,transports=transports,
                source_pair=[233,239],image_pair=[5557,238],
                forced_colors=[[[int(old['words'][a][p]) for p in [233,239]],
                                [int(old['words'][a][p]) for p in [5557,238]]] for a in range(5)],
                unequal_counts=[4,0],denominator=5,
                scope='All finite nilpotent-monodromy covers of the exact E083 word/palette actions; not arbitrary full-joint.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output')
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    destination=Path(args.output) if args.output else root/'certificates/joint_nilpotent_cover.json'
    data=build(root);destination.write_text(json.dumps(data,separators=(',',':'))+'\n')
    print(json.dumps(dict(status='BUILT',path=str(destination),determinants=[[m['determinant'] for m in p['minors']] for p in data['parts']]),indent=2))
