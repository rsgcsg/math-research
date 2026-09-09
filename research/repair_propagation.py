"""Export a small direct list-forcing proof, not a solver status certificate."""
from collections import defaultdict, deque
from pathlib import Path
import gzip
import hashlib
import json

from finite_background_repair import prepare, ROOT
from multicenter_cores import transform, induced
from parts_core import clauses


def certificate(layers=2):
    core,words,cross,equal,neighbors,bg,patch=prepare()
    for _ in range(layers): patch.update(w for v in tuple(patch) for w in neighbors(v))
    ca=defaultdict(list);eq=defaultdict(list)
    for a,b in sorted(cross):ca[a].append(b);ca[b].append(a)
    for a,b in sorted(equal):eq[a].append(b);eq[b].append(a)
    removed={};masks=defaultdict(int);queue=deque();events=[];contradiction=None
    def forbid(v,c,kind,w,deps=()):
        nonlocal contradiction
        if (v,c) in removed:return
        removed[v,c]=len(events);events.append((v,c,kind,w,tuple(deps)))
        masks[v] |= 1<<c;queue.append((v,c))
        if masks[v] == 31:contradiction=v
    for v in sorted(patch):
        for w in neighbors(v):
            if w not in patch:forbid(v,bg(w),'boundary',w)
        if contradiction:break
    while queue and contradiction is None:
        v,c=queue.popleft()
        for w in eq[v]:forbid(w,c,'equality',v,(removed[v,c],))
        if masks[v].bit_count() == 4:
            remaining=next(t for t in range(5) if not masks[v] & (1<<t))
            deps=tuple(removed[v,t] for t in range(5) if t != remaining)
            for w in list(neighbors(v))+ca[v]:
                if w in patch:forbid(w,remaining,'edge',v,deps)
        if contradiction:break
    assert contradiction is not None,'No propagation certificate found'
    needed=set();todo=[removed[contradiction,c] for c in range(5)]
    while todo:
        i=todo.pop()
        if i not in needed:needed.add(i);todo.extend(events[i][4])
    order=sorted(needed);remap={old:new for new,old in enumerate(order)}
    proof=[dict(vertex=v,color=c,kind=kind,neighbor=w,parents=[remap[p] for p in deps])
           for i in order for v,c,kind,w,deps in (events[i],)]
    # A separate, unrestricted coloring establishes what this conditioned
    # obstruction does NOT say about the actual finite unit-distance graph.
    from pysat.solvers import Solver
    labels=sorted({v for row in proof for v in (row['vertex'],row['neighbor'])})
    points=[];point_ids={};aliases=[]
    for s,m,n,q in labels:
        p=transform(core['points'][q],((16*(2*m+n),)+(0,)*7,(0,16*n)+(0,)*6),s)
        if p not in point_ids:point_ids[p]=len(points);points.append(p)
        aliases.append(point_ids[p])
    edges,_=induced(points,768)
    with Solver(name='cadical195',bootstrap_with=clauses(len(points),edges,3)) as solver:
        solver.conf_budget(100000);status=solver.solve_limited()
        assert status is True,'The diagnostic graph was not certified three-colorable'
        model=set(solver.get_model())
        word=''.join(str(next(c for c in range(3) if 3*v+c+1 in model)) for v in range(len(points)))
    return dict(schema=1,layers=layers,background_words=words,patch_vertices=len(patch),
                input_sha256={name:hashlib.sha256((ROOT/'certificates'/name).read_bytes()).hexdigest()
                              for name in ('parts509_core.json','refined_center_arrays.json.gz','multicenter_cores.json')},
                conclusion_vertex=contradiction,proof=proof,
                finite_graph=dict(labels=labels,aliases=aliases,vertices=len(points),edges=len(edges),three_coloring=word),
                scope='No five-coloring equal to this background outside this specified patch; not a host lower bound')


if __name__ == '__main__':
    result=certificate()
    (ROOT/'certificates/finite_background_obstruction.json.gz').write_bytes(
        gzip.compress(json.dumps(result,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(dict(events=len(result['proof']),patch_vertices=result['patch_vertices'],
                         conclusion_vertex=result['conclusion_vertex'])))
