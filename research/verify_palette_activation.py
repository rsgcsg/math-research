"""Independent geometry for complete 5x5 contact matrices and local mobility."""
from functools import lru_cache
from itertools import product,combinations
from pathlib import Path
import json
import hashlib
import gzip

from verify_multicenter_cores import rotate_at,unit


def verify(root,data_override=None):
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    data=data_override if data_override is not None else json.loads((root/'certificates/palette_activation_obstruction.json').read_text())
    assert data['input_sha256']=={name:hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()
                                for name in ('parts509_core.json','multicenter_cores.json')}
    words=json.loads((root/'certificates/multicenter_cores.json').read_text())['both_arrays_coloring']['three_core_words']
    assert data['schema']==1 and data['background_words']==words
    points=[tuple(map(tuple,p)) for p in core['points']];ids={p:q for q,p in enumerate(points)}
    @lru_cache(None)
    def point(v):
        s,m,n,q=v
        assert s in (-1,1) and 0<=q<509
        return rotate_at(points[q],((16*(2*m+n),)+(0,)*7,(0,16*n)+(0,)*6),s)
    def color(v):
        s,m,n,q=v
        return (int(words[1 if s==1 else 2][q])+m%3)%5
    seen=set()
    for row in data['witnesses']:
        a,b=row['old_colors'];u,v=map(tuple,row['endpoints']);kind=row['relation']
        assert u[0]==-1 and v[0]==1 and color(u)==a and color(v)==b
        assert (a,b,kind) not in seen;seen.add((a,b,kind))
        if kind=='unit':assert unit(point(u),point(v),768)
        elif kind=='equal':assert point(u)==point(v)
        else:raise AssertionError(kind)
    assert seen==set(product(range(5),range(5),('unit','equal')))
    movable=set();neighbor_checks=0
    for row in data['movable']:
        v=tuple(row['vertex']);s,m,n,q=v;old=row['old'];new=row['new']
        assert (m,n)==(0,0) and color(v)==old and old!=new and new in range(5)
        assert (s,old) not in movable;movable.add((s,old))
        # Complete same-center unit pairs; no listed-edge assumption here.
        neighbors={(s,0,0,r) for r in range(509) if unit(point(v),point((s,0,0,r)),768)}
        # T060's two cross-center cases, independently recovered by membership.
        for dm,dn in product(range(-4,5),repeat=2):
            length=dm*dm+dm*dn+dn*dn
            if length==12:neighbors.add((s,dm,dn,q))
            if length==9:
                a,b=map(list,points[q]);a[0]+=16*(2*dm+dn);b[1]+=16*dn
                r=ids.get((tuple(a),tuple(b)))
                if r is not None:neighbors.add((s,dm,dn,r))
        for w in neighbors:
            assert unit(point(v),point(w),768) and color(w)!=new
            neighbor_checks+=1
    assert movable==set(product((-1,1),range(5)))
    # The search's voltage-component calculations are deliberately NOT trusted:
    # every rejection used a fixed-endpoint relation before any SAT search.
    direct_rejections=0
    for name,double in (('kempe_background.json.gz',False),('kempe_double_background.json.gz',True)):
        record=json.loads(gzip.decompress((root/'certificates'/name).read_bytes()))
        assert record['background_words']==words and record['double']==double
        schemes=[(p,) for p in combinations(range(5),2)]
        if double:
            schemes=[]
            for single in range(5):
                rest=sorted(set(range(5))-{single})
                for other in rest[1:]:schemes.append(((rest[0],other),tuple(c for c in rest if c not in (rest[0],other))))
        observed=set()
        for row in record['observations']:
            pair=tuple(tuple(map(tuple,side)) for side in row['pairs'])
            assert pair not in observed;observed.add(pair)
            assert row['status']=='FIXED_CONSTRAINT_OBSTRUCTION'
            witness=row['witness'];u,v=map(tuple,witness['endpoints'])
            assert u[0] in (-1,1) and v[0] in (-1,1)
            for endpoint,c in zip((u,v),witness['colors']):
                assert c==color(endpoint)
                assert all(c not in colors for colors in pair[0 if endpoint[0]==1 else 1])
            if witness['equality']:
                assert point(u)==point(v) and color(u)!=color(v)
            else:
                assert unit(point(u),point(v),768) and color(u)==color(v)
            direct_rejections+=1
        assert observed==set(product(schemes,repeat=2))
    return dict(status='PASS',unit_witnesses=25,equality_witnesses=25,
                independently_movable_color_classes=10,complete_neighbor_checks=neighbor_checks,
                direct_color_pair_schemes_rejected=direct_rejections,
                scope='Fixed background partitions only; at least one orientation must split all five classes')


if __name__=='__main__':
    if not __debug__:raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
