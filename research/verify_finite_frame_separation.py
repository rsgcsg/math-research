"""Independent T133-T134 / E103-E104 certificate replay; standard library only.

No builder, subgroup search, DSU, SMT, or SAT solver is imported. Exact geometry
is independently reconstructed by the pre-existing verifier. The general
all-word and all-cover claims additionally use the written mathematical proof.
"""
from array import array
from collections import Counter, deque
from itertools import combinations, permutations, product
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json
import math
from verify_joint_nilpotent_cover import prepare
from verify_quintic_core_probe import conjugate_twice, multiplication_twice


def digest(x):
    return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()

def permutation(a,k):
    assert isinstance(a,(list,tuple)) and len(a)==k
    assert all(type(x) is int for x in a) and sorted(a)==list(range(k))

def compose(a,b):
    return tuple(a[b[c]] for c in range(len(a)))

def inverse(a):
    return tuple(a.index(c) for c in range(len(a)))

def closure(generators,k):
    seen={tuple(range(k))}; queue=deque(seen)
    while queue:
        a=queue.popleft()
        for b in generators:
            v=compose(a,b)
            if v not in seen:
                seen.add(v); queue.append(v)
    return seen

def derived_orders(group,k):
    orders=[]; group=set(map(tuple,group))
    while True:
        orders.append(len(group))
        if len(group)==1:
            return orders
        generators={compose(compose(inverse(a),inverse(b)),compose(a,b)) for a in group for b in group}
        following=closure(generators,k)
        assert following < group, 'Group is not verified solvable'
        group=following

def headers(data,prepared,schema,experiment):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema']==schema and data['experiment']==experiment
    assert data['geometry']==prepared['report']['geometry']
    assert data['source_sha256']==prepared['source_sha256']

def local_transitions(prepared,degree,fibers):
    n=len(prepared['context']['points']); old=prepared['old']; sigma=[]; palettes=[]
    for j in range(14):
        s=[degree*old['word_permutations'][j][a]+fibers[j][a][t]
           for a in range(5) for t in range(degree)]
        p=[old['color_permutations'][j][a] for a in range(5) for _ in range(degree)]
        sigma.extend([s,list(inverse(s))]); palettes.extend([p,None])
        palettes[-1]=[list(inverse(p[sigma[-1][a]])) for a in range(5*degree)]
    outgoing=[[] for _ in range(n)]
    for j,mapping in enumerate(prepared['maps'][:14]):
        for p,q in mapping:
            outgoing[p].append((2*j,q)); outgoing[q].append((2*j+1,p))
    return outgoing,sigma,palettes

def check_separator_structure(data,prepared):
    headers(data,prepared,'finite-frame-separator-v1','E103')
    fibers=data['permutations']; assert len(fibers)==14
    for row in fibers:
        assert len(row)==5
        for item in row:
            permutation(item,3)
    assert fibers[2][:4]==[[0,1,2]]*4
    monodromy=closure([p for row in fibers for p in row],3)
    assert len(monodromy)==6  # Tree edge lifts are identity, so chord labels generate it.
    n=len(prepared['context']['points']); old=prepared['old']
    outgoing,sigma,palettes=local_transitions(prepared,1,[[[0]]*5 for _ in range(14)])
    entries=data['component_labels']; values={}
    for entry in entries:
        assert isinstance(entry,list) and len(entry)==2
        node,value=entry
        assert type(node) is int and 0<=node<25*n and node not in values
        assert type(value) is int and 0<=value<3
        values[node]=value
    assert list(values)==sorted(values)
    root=data['root']; target=data['target']
    assert root==(0*n+5557)*5+1 and target==(0*n+238)*5+1
    assert values[root]==0 and values[target]!=0
    visited={root}; queue=deque([root]); directed=0
    while queue:
        node=queue.popleft(); a,p=divmod(node//5,n); c=node%5
        for step,q in outgoing[p]:
            b=sigma[step][a]; d=palettes[step][a][c]; other=(b*n+q)*5+d
            assert other in values
            j=step//2
            action=fibers[j][a] if step%2==0 else inverse(fibers[j][b])
            assert values[other]==action[values[node]]
            directed+=1
            if other not in visited:
                visited.add(other); queue.append(other)
    assert visited==set(values)
    expected=data['expected']
    assert expected['component_vertices']==len(visited)==24235
    assert expected['directed_component_edges']==directed==117150
    assert expected['cover_degree']==3 and expected['monodromy_order']==len(monodromy)
    return dict(component_vertices=len(visited),directed_component_edges=directed,
                root_fiber=values[root],target_fiber=values[target],monodromy_order=len(monodromy))

def derive_separator_clauses(data,prepared):
    """Full lifted equality components by independent BFS, then Boolean rules."""
    n=len(prepared['context']['points']); m=15
    outgoing,sigma,palettes=local_transitions(prepared,3,data['permutations'])
    labels=array('I',[0])*(m*n*5); number=0
    for root in range(len(labels)):
        if labels[root]:
            continue
        number+=1; labels[root]=number; queue=deque([root])
        while queue:
            node=queue.popleft(); a,p=divmod(node//5,n); c=node%5
            for step,q in outgoing[p]:
                other=(sigma[step][a]*n+q)*5+palettes[step][a][c]
                if not labels[other]:
                    labels[other]=number; queue.append(other)
    def color(a,p,c):
        return labels[(a*n+p)*5+c]
    clauses=set()
    for a in range(m):
        for p in range(n):
            cs=[color(a,p,c) for c in range(5)]
            clauses.add(tuple(sorted(set(cs))))
            for c,d in combinations(cs,2):
                clauses.add(tuple(sorted({-c,-d})))
        for p,q in prepared['context']['edges']:
            for c in range(5):
                clauses.add(tuple(sorted({-color(a,p,c),-color(a,q,c)})))
    clauses=sorted(clauses); assignment={}; trace=[]
    while True:
        before=len(assignment)
        for index,clause in enumerate(clauses):
            if any(assignment.get(abs(lit))==(lit>0) for lit in clause):
                continue
            free=[lit for lit in clause if abs(lit) not in assignment]
            assert free, 'Unexpected contradictory old14 model'
            if len(free)==1:
                literal=free[0]; assignment[abs(literal)]=literal>0
                trace.append([index,literal])
        if len(assignment)==before:
            break
    # Independently replay the implication trace, without the generating scan.
    checked={}
    for index,literal in trace:
        clause=clauses[index]
        assert literal in clause and abs(literal) not in checked
        assert all(x==literal or (abs(x) in checked and checked[abs(x)]!=(x>0)) for x in clause)
        checked[abs(literal)]=literal>0
    assert checked==assignment
    forced=[]
    for a in range(m):
        word=[]
        for p in [233,239,5557,238]:
            truth=[checked.get(color(a,p,c)) for c in range(5)]
            assert truth.count(True)==1 and truth.count(False)==4
            word.append(truth.index(True))
        forced.append(word)
    source=sum(w[0]!=w[1] for w in forced); image=sum(w[2]!=w[3] for w in forced)
    assert [dict(prepared['maps'][14])[p] for p in [233,239]]==[5557,238]
    # Non-vacuity: repeat the five saved proper words over the three fibers.
    words=[prepared['old']['words'][a] for a in range(5) for _ in range(3)]
    assert all(w[p]!=w[q] for w in words for p,q in prepared['context']['edges'])
    for j,mapping in enumerate(prepared['maps'][:14]):
        for a,w in enumerate(words):
            assert all(int(words[sigma[2*j][a]][q])==palettes[2*j][a][int(w[p])] for p,q in mapping)
        def partition(w,indices):
            seen={}; return tuple(seen.setdefault(w[x],len(seen)) for x in indices)
        assert Counter(partition(w,[p for p,q in mapping]) for w in words)==Counter(partition(w,[q for p,q in mapping]) for w in words)
    # The requested literals really are different classes despite both being forced true.
    assert color(0,5557,1)!=color(0,238,1)
    assert checked[color(0,5557,1)] is True and checked[color(0,238,1)] is True
    return dict(literal_classes=number,proper_clauses=len(clauses),forced_literals=len(checked),
                unequal_counts=[source,image],support=m,forced_colors=forced,
                clause_sha256=digest(clauses),unit_trace_sha256=digest(trace),
                independently_replayed_unit_steps=len(trace),
                repeated_old_word_edge_checks=m*len(prepared['context']['edges']))

def check_separator_consequence(data,derived):
    for key in ['literal_classes','proper_clauses','forced_literals','unequal_counts','support']:
        assert data['expected'][key]==derived[key]
    assert derived['unequal_counts']==[12,0] and derived['forced_literals']==195


def check_arithmetic(data,prepared):
    headers(data,prepared,'arithmetic-frame-separation-v1','E104')
    p=data['prime']; assert type(p) is int and p==5701
    assert all(p%d for d in range(2,math.isqrt(p)+1))
    images=data['images']; bars=data['bars']
    for a in [images,bars]:
        assert len(a)==32 and all(type(x) is int and 0<=x<p for x in a)
        assert a[0]==1
    table=multiplication_twice(); products=0
    for (i,j),row in table.items():
        for embedding in [images,bars]:
            assert sum(c*embedding[k] for k,c in row)%p==2*embedding[i]*embedding[j]%p
            products+=1
    for j in range(32):
        bar_basis=conjugate_twice([int(i==j) for i in range(32)])
        assert sum(x*y for x,y in zip(bar_basis,images))%p==2*bars[j]%p
    coords=[]
    for point in prepared['context']['points']:
        assert all(x.denominator%p for x in point)
        coords.append([sum(x.numerator*pow(x.denominator,-1,p)*y for x,y in zip(point,e))%p for e in [images,bars]])
    assert len(set(map(tuple,coords)))==len(coords)==data['expected']['injective_points']==10077
    assert digest(coords)==data['coordinate_sha256']
    actions=data['actions']; assert len(actions)==len(prepared['maps'])==15
    domains=[]; obligations=0
    for j,(action,mapping) in enumerate(zip(actions,prepared['maps'])):
        a=action['scale']; t=action['shift']; reflected=action['reflection']
        assert type(a) is int and 0<a<p and type(reflected) is bool
        assert reflected==(j in [4,13])
        assert len(t)==2 and all(type(x) is int and 0<=x<p for x in t)
        for source,target in mapping:
            x,y=coords[source]
            if reflected:
                x,y=y,x
            assert [(a*x+t[0])%p,(pow(a,-1,p)*y+t[1])%p]==coords[target]
            obligations+=1
        domains.append(len(mapping))
    assert domains==data['expected']['motion_domains']
    for i,j in prepared['context']['edges']:
        assert (coords[i][0]-coords[j][0])*(coords[i][1]-coords[j][1])%p==1
    old=prepared['old']; sig=old['word_permutations']; pi=old['color_permutations']; gauge=data['gauge']
    assert len(gauge)==5
    for q in gauge:
        permutation(q,5)
    assert gauge[0]==list(range(5))
    for a in range(4):
        assert tuple(gauge[sig[2][a]])==compose(pi[2][a],gauge[a])
    generators=[compose(inverse(gauge[sig[j][a]]),compose(pi[j][a],gauge[a])) for j in range(14) for a in range(5)]
    group=closure(generators,5)
    assert sorted(group)==list(map(tuple,data['palette_group']))
    assert len(group)==data['expected']['palette_order']==24
    fixed=[c for c in range(5) if all(g[c]==c for g in group)]
    assert fixed==data['expected']['palette_fixed_colors']==[4]
    orders=derived_orders(group,5)
    assert orders==data['expected']['derived_orders']==[24,12,4,1]
    assert data['expected']['affine_group_order']==2*p*p*(p-1)
    assert data['expected']['cover_states']==5*2*p*p*(p-1)*len(group)==44461916568000
    return dict(prime=p,injective_points=len(coords),field_product_checks=products,
                full_motion_checks=obligations,motion_domains=domains,
                unit_edge_residue_checks=len(prepared['context']['edges']),
                palette_group_order=len(group),palette_fixed_colors=fixed,derived_orders=orders,
                symbolic_cover_states=data['expected']['cover_states'],
                scope='All 15 equation systems admit an injective same-state invariant; no 15-domain proper coloring is supplied.')


def calibrate_frames():
    """Tiny complete finite models, not substitutes for the general proof."""
    # Three physical vertices, one partial transposition and one partial 3-cycle.
    triangle=[(Fraction(0),Fraction(0)),(Fraction(1),Fraction(0)),(Fraction(1,2),Fraction(1,2))]
    assert all((x-u)**2+3*(y-v)**2==1 for (x,y),(u,v) in combinations(triangle,2))
    N=3; k=3; perms=list(permutations(range(3))); identity=tuple(range(3))
    generators=[(1,0,2),(1,2,0)]; palettes=[(1,2,0),(0,2,1)]
    pairs=[[(0,1),(1,0)],[(0,1),(1,2)]]
    nodes=list(product(perms,perms,range(N),range(k)))
    checks=0
    def inv_label(g,lam,x,c):
        return (g.index(x),lam.index(c))
    for g,lam,x,c in nodes:
        for j,mapping in enumerate(pairs):
            for a,b in mapping:
                if x==a:
                    gg=compose(generators[j],g); ll=compose(palettes[j],lam)
                    assert inv_label(g,lam,a,c)==inv_label(gg,ll,b,palettes[j][c])
                    checks+=1
    # The same actual unit triangle: trivial support with matching palettes,
    # and all six frames with identity palettes.
    for geom in generators:
        assert all(identity[geom[x]]==geom[identity[x]] for x in range(3))
    for word in perms:
        for geom in generators:
            next_word=compose(word,inverse(geom))
            assert all(next_word[geom[x]]==word[x] for x in range(3))
    assert len(closure(generators,3))==6
    # Finite affine model at p=5; test every pair of its 200 transformations.
    p=5
    affine=list(product(range(1,p),range(p),range(p),range(2)))
    def act(g,z):
        a,t,u,e=g; x,y=z
        if e: x,y=y,x
        return ((a*x+t)%p,(pow(a,-1,p)*y+u)%p)
    def mul(g,h):
        a,t,u,e=g; b,v,w,f=h
        xy=act(g,(v,w))
        return (a*(pow(b,-1,p) if e else b)%p,xy[0],xy[1],e^f)
    affine_set=set(affine)
    for g in affine:
        for h in affine:
            gh=mul(g,h); assert gh in affine_set
            for z in [(0,0),(1,0),(0,1)]:
                assert act(gh,z)==act(g,act(h,z))
        for x,y in product(range(p),repeat=2):
            a=act(g,(x,y)); b=act(g,(0,0))
            assert (a[0]-b[0])*(a[1]-b[1])%p==x*y%p
    return dict(frame_edges=checks,triangle_frames=6,triangle_exact_distances=3,affine_group_order=len(affine),affine_products=len(affine)**2)


def verify(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    prepared=prepare(root)
    separator=json.loads(gzip.decompress((root/'certificates/finite_frame_separator.json.gz').read_bytes()))
    arithmetic=json.loads((root/'certificates/arithmetic_frame_separation.json').read_text())
    structure=check_separator_structure(separator,prepared)
    derived=derive_separator_clauses(separator,prepared)
    check_separator_consequence(separator,derived)
    return dict(status='PASS',theorems=['T133','T134'],experiments=['E103','E104'],
                separator=dict(structure=structure,proper_consequence=derived),
                arithmetic_frame=check_arithmetic(arithmetic,prepared),calibrations=calibrate_frames())

if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
