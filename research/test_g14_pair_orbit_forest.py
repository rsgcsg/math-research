#!/usr/bin/env python3
"""Mutation tests for the added simple-spanning-tree check; stdlib only."""
import gzip, importlib.util, json
from pathlib import Path
HERE=Path(__file__).parent
BASE=HERE.parent/'certificates'
source=HERE/'verify_g14_pair_orbit_law.py'
spec=importlib.util.spec_from_file_location('review_checker',source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
basis=module.read(BASE/'g14_pair_orbit_basis.json.gz')[0]
geom=json.load(gzip.open(BASE/'Y_full_geometry.json.gz','rt'))
nodes={g:{tuple(p) for p in pairs} for g,pairs in basis['orbit_nodes_by_grade'].items()}
rows=basis['forest_edges']
assert module.check_forest_rows(rows,nodes)['1/sqrt3']['edges']==1859
assert module.check_forest_rows(rows,nodes)['2']['edges']==779
print('baseline forest: PASS')

def expect_rejection(label,mutated,phrase):
    try: module.check_forest_rows(mutated,nodes)
    except AssertionError as e:
        assert phrase in str(e),(label,str(e))
        print(label+': rejected as expected ('+phrase+')')
    else: raise AssertionError(label+' was accepted')

# Preserve per-grade row count but duplicate one d^2=4 edge.
qrows=[r for r in rows if r['grade']=='2']
mut=list(rows); idx=mut.index(qrows[-1]);mut[idx]=dict(qrows[0])
expect_rejection('duplicate-row mutation',mut,'duplicate forest row')

# Find a leaf edge and a valid non-tree motion edge within the remaining component.
grade='1/sqrt3'; grade_rows=[(i,r) for i,r in enumerate(rows) if r['grade']==grade]
adj={p:set() for p in nodes[grade]}
for i,r in grade_rows:
    a,b=tuple(r['source']),tuple(r['target']);adj[a].add(i);adj[b].add(i)
leaf_i,leaf_row=next((i,r) for i,r in grade_rows if len(adj[tuple(r['source'])])==1 or len(adj[tuple(r['target'])])==1)
leaf=tuple(leaf_row['source']) if len(adj[tuple(leaf_row['source'])])==1 else tuple(leaf_row['target'])
remaining=nodes[grade]-{leaf}
tree_edges={(min(tuple(r['source']),tuple(r['target'])),max(tuple(r['source']),tuple(r['target']))) for r in rows if r['grade']==grade}
fwd=[dict(m) for m in geom['mappings']]
chord=None
for j,f in enumerate(fwd):
    for a,b in nodes[grade]:
        if a in f and b in f:
            target=tuple(sorted((f[a],f[b])))
            if target in remaining and (min((a,b),target),max((a,b),target)) not in tree_edges:
                chord={'grade':grade,'motion':j,'source':[a,b],'target':list(target),'direction':'forward'};break
    if chord:break
assert chord is not None
# Removing the leaf edge and adding an internal chord produces both a cycle and a disconnection.
mut=[r for i,r in enumerate(rows) if i!=leaf_i]+[chord]
expect_rejection('cycle mutation',mut,'forest cycle')
# A missing leaf edge alone must be rejected for disconnectedness.
mut=[r for i,r in enumerate(rows) if i!=leaf_i]
expect_rejection('disconnected mutation',mut,'forest disconnected')
