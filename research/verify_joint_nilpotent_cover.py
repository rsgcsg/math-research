"""E101 independent exact checker (Python standard library only).

Rebuilds actual geometry through the pre-existing independent verifier. Each
certificate path is followed as actual partial motions with the saved palette
actions. Integer determinants, not ranks modulo sampled primes, certify the
full integral cycle lattice. No SAT, producer, NumPy, SymPy, or DSU is imported.
The unbounded-cover conclusion also uses the accompanying mathematical proof.
"""
from collections import deque
from fractions import Fraction
from pathlib import Path
import copy
import hashlib
import json
import math
from verify_quintic_tau_union import verify as geometry
from verify_quintic_core_probe import conjugate_twice, digest
from verify_dyadic_fixed_representation import _definitions


def determinant(matrix):
    """Fraction-free elimination with exact divisions and row pivoting."""
    n=len(matrix)
    assert n and all(len(row)==n and all(type(x) is int for x in row) for row in matrix)
    a=[row[:] for row in matrix];previous=1;sign=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n) if a[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:a[k],a[pivot]=a[pivot],a[k];sign=-sign
        value=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=a[i][j]*value-a[i][k]*a[k][j]
                assert numerator%previous==0
                a[i][j]=numerator//previous
            a[i][k]=0
        previous=value
    return sign*a[-1][-1]


def prepare(root):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    report,context=geometry(root,geometry_context=True)
    raw=(root/'certificates/quintic_multiword_return_joint.json').read_bytes()
    source=json.loads(raw);old=source['result'];assert source['geometry']==report['geometry']
    points=context['points'];n=len(points);den=math.lcm(*(x.denominator for p in points for x in p))
    integers=[tuple(int(x*den) for x in p) for p in points];lookup={p:i for i,p in enumerate(integers)}
    mul=context['ring']['mul'];basis=[tuple(Fraction(i==j) for i in range(32)) for j in range(32)]
    maps=[];definitions=_definitions(context)
    for name,a,shift,reflection in definitions:
        cols=[mul(a,tuple(Fraction(x,2) for x in conjugate_twice(e)) if reflection else e) for e in basis]
        scale=math.lcm(*(x.denominator for col in cols for x in col),*((x*den).denominator for x in shift))
        sparse=[[(i,int(x*scale)) for i,x in enumerate(col) if x] for col in cols]
        offset=[int(x*den*scale) for x in shift];mapping=[]
        for p,point in enumerate(integers):
            target=offset[:]
            for coefficient,column in zip(point,sparse):
                if coefficient:
                    for i,value in column:target[i]+=coefficient*value
            if any(x%scale for x in target):continue
            target=tuple(x//scale for x in target)
            if target in lookup:mapping.append((p,lookup[target]))
        maps.append(mapping)
    assert old['motions']==[d[0] for d in definitions[:14]]
    assert [digest(m) for m in maps[:14]]==old['mapping_sha256']
    assert len(maps[14])==29
    return dict(report=report,context=context,old=old,maps=maps,
                source_sha256=hashlib.sha256(raw).hexdigest())


def toy_nonnilpotent():
    """Integral H1-surjectivity does NOT suffice for arbitrary finite covers."""
    permutations=[(0,2,1),(1,2,0)]  # a fixes 0; b is a three-cycle.
    cycles=[[1],[2,1,2],[2,2,2]];vectors=[]
    for word in cycles:
        x=0;v=[0,0]
        for edge in word:x=permutations[edge-1][x];v[edge-1]+=1
        assert x==0;vectors.append(v)
    ds=[determinant([vectors[0],vectors[i]]) for i in [1,2]]
    assert ds==[2,3] and math.gcd(*ds)==1
    remaining={(i,j) for i in range(3) for j in range(3)};sizes=[]
    while remaining:
        start=min(remaining);seen={start};queue=deque([start])
        while queue:
            i,j=queue.popleft()
            for p in permutations:
                pair=(p[i],p[j])
                if pair not in seen:seen.add(pair);queue.append(pair)
        remaining-=seen;sizes.append(len(seen))
    assert sorted(sizes)==[3,6]
    return dict(base_vertices=1,base_edges=2,cover_sheets=3,minor_determinants=ds,
                pullback_components=sorted(sizes),scope='Combinatorial S3 counterexample, not a unit-distance obstruction')


def check_data(data, prepared):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    assert data['schema']=='joint-nilpotent-cover-v1' and data['experiment']=='E101'
    assert data['source_sha256']==prepared['source_sha256']
    assert data['geometry']==prepared['report']['geometry']
    old=prepared['old'];n=len(prepared['context']['points']);maps=prepared['maps']
    forward=[dict(m) for m in maps[:14]];backward=[{y:x for x,y in m} for m in maps[:14]]
    sigma=old['word_permutations'];pi=old['color_permutations']
    endpoints=[(a,sigma[j][a]) for j in range(14) for a in range(5)]
    assert data['base_vertices']==5 and data['base_edges']==len(endpoints)==70
    tree=data['tree_edges'];assert len(tree)==4 and len(set(tree))==4
    connected={0}
    while True:
        before=len(connected)
        for e in tree:
            assert type(e) is int and 0<=e<70
            a,b=endpoints[e]
            if a in connected or b in connected:connected.update([a,b])
        if len(connected)==before:break
    assert len(connected)==5  # Four edges connecting five vertices are a tree.
    chords=[e for e in range(70) if e not in tree]
    def unpack(v):
        assert type(v) is int and 0<=v<25*n
        a,p=divmod(v//5,n);return a,p,v%5
    def walk(start,word):
        a,p,c=unpack(start);counts=[0]*70
        assert isinstance(word,list)
        for step in word:
            assert type(step) is int and 1<=abs(step)<=70
            label=abs(step)-1;j,source=divmod(label,5);target=sigma[j][source]
            if step>0:
                assert a==source and p in forward[j]
                a,p,c=target,forward[j][p],pi[j][source][c];counts[label]+=1
            else:
                assert a==target and p in backward[j]
                a,p,c=source,backward[j][p],pi[j][source].index(c);counts[label]-=1
        return (a*n+p)*5+c,counts
    parts=data['parts'];assert len(parts)==3 and [p['seed'] for p in parts]==[155,156,159]
    determinants=[];steps=0;number_cycles=0
    for part in parts:
        rows=[]
        for word in part['cycles']:
            endpoint,row=walk(part['seed'],word);assert endpoint==part['seed']
            boundary=[0]*5
            for coefficient,(a,b) in zip(row,endpoints):boundary[a]-=coefficient;boundary[b]+=coefficient
            assert boundary==[0]*5
            rows.append([row[e] for e in chords]);steps+=len(word);number_cycles+=1
        ds=[]
        for minor in part['minors']:
            ids=minor['cycles'];assert len(ids)==66 and len(set(ids))==66
            assert all(type(i) is int and 0<=i<len(rows) for i in ids)
            d=determinant([rows[i] for i in ids]);assert type(minor['determinant']) is int
            assert d==minor['determinant'] and d!=0;ds.append(d)
        assert ds and math.gcd(*ds)==1;determinants.append(ds)
    classes={}
    for item in data['transports']:
        node,part=item['node'],item['component'];assert type(part) is int and 0<=part<3
        endpoint,_=walk(parts[part]['seed'],item['path']);assert endpoint==node and node not in classes
        classes[node]=part;steps+=len(item['path'])
    literal=lambda a,p,c:(a*n+p)*5+c
    assert [classes[literal(0,31,c)] for c in range(5)]==[0,1,0,0,2]
    assert classes[literal(0,193,4)]==2
    assert (31,193) in prepared['context']['edges']
    # A is false by repeated colors at point 31; C by the edge 31--193;
    # then B is true by the exactly-one condition at point 31.
    truth=[False,True,False]
    source_pair=data['source_pair'];image_pair=data['image_pair']
    assert source_pair==[233,239] and image_pair==[5557,238]
    assert [dict(maps[14])[p] for p in source_pair]==image_pair
    colors=[]
    for a in range(5):
        record=[]
        for pair in [source_pair,image_pair]:
            labels=[]
            for p in pair:
                values=[truth[classes[literal(a,p,c)]] for c in range(5)]
                assert sum(values)==1;labels.append(values.index(True))
            record.append(labels)
        colors.append(record)
    assert colors==data['forced_colors']
    counts=[sum(record[s][0]!=record[s][1] for record in colors) for s in range(2)]
    assert counts==data['unequal_counts']==[4,0] and data['denominator']==5
    return dict(status='PASS',experiment='E101',geometry=data['geometry'],
                integral_cycle_rank=66,minor_determinants=determinants,
                checked_closed_walks=number_cycles,checked_path_steps=steps,
                checked_transports=len(classes),forced_colors=colors,unequal_counts=counts,
                toy=toy_nonnilpotent(),scope=data['scope'])


def verify(root,certificate=None,mutations=False):
    root=Path(root);path=Path(certificate) if certificate else root/'certificates/joint_nilpotent_cover.json'
    data=json.loads(path.read_text());prepared=prepare(root);report=check_data(data,prepared)
    if mutations:
        cases=[]
        def changed(name,fn):
            bad=copy.deepcopy(data);fn(bad);cases.append((name,bad))
        changed('source',lambda d:d.update(source_sha256='0'*64))
        changed('geometry',lambda d:d['geometry'].update(vertices=1))
        changed('tree',lambda d:d.update(tree_edges=[10,10,12,13]))
        changed('seed',lambda d:d['parts'][0].update(seed=156))
        changed('walk',lambda d:d['parts'][0]['cycles'][0].append(71))
        changed('determinant',lambda d:d['parts'][0]['minors'][0].update(determinant=1))
        changed('missing_saturation',lambda d:d['parts'][0].update(minors=d['parts'][0]['minors'][:1]))
        changed('minor_dimension',lambda d:d['parts'][0]['minors'][0]['cycles'].pop())
        changed('transport',lambda d:d['transports'][0].update(component=(d['transports'][0]['component']+1)%3))
        changed('event',lambda d:d.update(image_pair=[5557,239]))
        changed('color',lambda d:d['forced_colors'][0][0].__setitem__(0,4))
        rejected=[]
        for name,bad in cases:
            try:check_data(bad,prepared)
            except (AssertionError,KeyError,IndexError,ValueError):rejected.append(name)
            else:raise AssertionError('Accepted mutation: '+name)
        report['mutations_rejected']=rejected
    return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('certificate',nargs='?');p.add_argument('--mutations',action='store_true');args=p.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1],args.certificate,args.mutations),indent=2))
