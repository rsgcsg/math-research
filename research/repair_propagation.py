"""Export a small direct list-forcing proof, not a solver status certificate."""
from collections import defaultdict, deque
from pathlib import Path
import gzip
import json

from finite_background_repair import prepare, ROOT


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
    return dict(schema=1,layers=layers,background_words=words,patch_vertices=len(patch),
                conclusion_vertex=contradiction,proof=proof,
                scope='No five-coloring equal to this background outside this specified patch; not a host lower bound')


if __name__ == '__main__':
    result=certificate()
    (ROOT/'certificates/finite_background_obstruction.json.gz').write_bytes(
        gzip.compress(json.dumps(result,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(dict(events=len(result['proof']),patch_vertices=result['patch_vertices'],
                         conclusion_vertex=result['conclusion_vertex'])))
