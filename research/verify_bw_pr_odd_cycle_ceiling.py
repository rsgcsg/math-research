#!/usr/bin/env python3
"""Exact known-node BW odd-cycle ceiling; no full15 feasibility claim."""
import argparse,hashlib,json,sys,collections,time
if not __debug__:
 raise RuntimeError("Verification requires assertions; run without -O")
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--write-receipt',action='store_true')
args=ap.parse_args()
import verify_pr_matching_window_ceiling as v
R=ROOT/'certificates'
g=v.read(R/'Y_full_geometry.json.gz');pb=v.read(R/'g14_pair_orbit_basis.json.gz');rb=v.read(R/'g14_r_pair_orbit_basis.json.gz')
n,E,P,Rp=v.validate_inputs(g,pb,rb);U=E|P|Rp
qt={e:0 for e in E};qt.update({e:1 for e in P});qt.update({e:2 for e in Rp})
adj=[set() for _ in range(n)]
for a,b in U:adj[a].add(b);adj[b].add(a)
t0=time.monotonic()
# Fixed positive node classes at both high-r vertices: A=r from (E,R), B=r-p from (P,R), C=p from (E,P).
A=[];B=[];C=[]
for j in range(n):
 for i in sorted(adj[j]):
  ti=qt[tuple(sorted((i,j)))]
  for k in sorted(adj[j]):
   if i==k:continue
   tk=qt[tuple(sorted((j,k)))]
   t=(i,j,k)
   if tk==2 and ti==0:A.append(t)
   elif tk==2 and ti==1:B.append(t)
   elif tk==1 and ti==0:C.append(t)
assert (len(A),len(B),len(C))==(78142,20968,70350)
print('node counts A B C',len(A),len(B),len(C),flush=True)
Aids={t:i for i,t in enumerate(A)};Bids={t:len(A)+i for i,t in enumerate(B)}
# Build A/B source conflict graph from exact positive/implied-negative pair relation; also preserve reps.
ABnodes=A+B; abid={t:i for i,t in enumerate(ABnodes)}
pos_map=collections.defaultdict(list);neg_map=collections.defaultdict(list)
def pp(x,y):return (x,y) if x<y else (y,x)
for u,(i,j,k) in enumerate(ABnodes):
 pos_map[pp(j,k)].append(u)
 neg_map[pp(i,j)].append(u);neg_map[pp(i,k)].append(u)
ab_edges=set()
for u,(i,j,k) in enumerate(ABnodes):
 for v_id in neg_map.get(pp(j,k),()):
  if u!=v_id:ab_edges.add((u,v_id) if u<v_id else (v_id,u))
print('AB source conflict edges',len(ab_edges),flush=True)
# Verify source edge forms against pair characterization on this actual subgraph.
shapes=set()
for u,(i,j,k) in enumerate(ABnodes):
 for l in adj[i]:
  for s in ((l,i,j),(l,i,k)):
   vv=abid.get(s)
   if vv is not None and vv!=u:shapes.add((u,vv) if u<vv else (vv,u))
 for l in adj[j]:
  s=(l,j,i);vv=abid.get(s)
  if vv is not None and vv!=u:shapes.add((u,vv) if u<vv else (vv,u))
 for l in adj[k]:
  s=(l,k,i);vv=abid.get(s)
  if vv is not None and vv!=u:shapes.add((u,vv) if u<vv else (vv,u))
assert shapes==ab_edges
# Classify AA, AB, BB edge families. A-A should be absent; AB edges weight=0; BB edge weight=1/27 at min vertex.
aa=[];ab=[];bb=[]
for u,vv in ab_edges:
 uA=u<len(A);vA=vv<len(A)
 if uA and vA:aa.append((u,vv))
 elif not uA and not vA:bb.append((u,vv))
 else:ab.append((u,vv))
assert not aa
assert (len(ab),len(bb),len(ab_edges))==(31178,5476,36654)
# Build zero A-B connected components; count isolated A-only separately.
zadj=[[] for _ in ABnodes]
for u,vv in ab:zadj[u].append(vv);zadj[vv].append(u)
comp=[-1]*len(ABnodes);cid=0;comp_sizes=[];comp_B=collections.Counter();comp_A=collections.Counter()
for s in range(len(ABnodes)):
 if comp[s]>=0:continue
 comp[s]=cid;Q=[s]
 for u in Q:
  for w in zadj[u]:
   if comp[w]<0:comp[w]=cid;Q.append(w)
   else:assert comp[w]==cid
 comp_sizes.append(len(Q));comp_B[cid]=sum(u>=len(A) for u in Q);comp_A[cid]=sum(u<len(A) for u in Q);cid+=1
assert all(vv<=1 for vv in comp_B.values())
assert all(len(zadj[u])<=1 for u in range(len(A)))
assert all(vv==1 for vv in comp_B.values() if vv>0)
assert all(comp_A[c]==1 for c in comp_B if comp_B[c]==0)
star_comps=sum(vv==1 for vv in comp_B.values());isolated_A=sum(comp_B[c]==0 and comp_A[c]==1 for c in comp_B)
Aonly_comps=sum(vv==0 for vv in comp_B.values())
assert Aonly_comps==isolated_A==46964 and star_comps==20968 and cid==67932
# B-B graph on unique B-centered zero components; preserve edges and representatives.
bgraph=collections.defaultdict(set);bb_edge_comps=set();bb_loops=[]
for u,vv in bb:
 cu,cv=comp[u],comp[vv]
 if cu==cv:bb_loops.append((u,vv,cu))
 else:
  ee=tuple(sorted((cu,cv)));bb_edge_comps.add(ee);bgraph[cu].add(cv);bgraph[cv].add(cu)
# Bipartite test, including every B-centered comp as an isolated vertex.
centers={comp[len(A)+i] for i in range(len(B))}
bipcol={};bip=False;bad_bedge=None
for s in centers:
 if s in bipcol:continue
 bipcol[s]=0;Q=[s]
 for u in Q:
  for w in bgraph.get(u,()):
   if u==w or (w in bipcol and bipcol[w]==bipcol[u]):bad_bedge=(u,w);break
   if w not in bipcol:bipcol[w]=bipcol[u]^1;Q.append(w)
  if bad_bedge:break
 if bad_bedge:break
bip=bad_bedge is None
assert not bb_loops and bip
print('AB components',cid,'B-centered',star_comps,'A-only',Aonly_comps,'isolated-A singletons',isolated_A,'B-B quotient edges',len(bb_edge_comps),'B-graph vertices',len(centers),'bipartite',bip,'largest zero comp',max(comp_sizes),flush=True)
# Check for one-C obstruction: C adjacent to A and B in same star, or C adjacent to A-nodes in both ends of a B-B edge.
# Build positive/negative maps for A/B nodes only; node s's implied negatives are ij, ik.
AB_pos=collections.defaultdict(list);AB_neg=collections.defaultdict(list)
for t,u in abid.items():
 i,j,k=t;AB_pos[pp(j,k)].append(u);AB_neg[pp(i,j)].append(u);AB_neg[pp(i,k)].append(u)
star_witness=None;five_witness=None;max_neigh=0;num_C=0
c_neighborhood_hash=hashlib.sha256()
source_c_edges=0
for i,j,k in C:
 num_C+=1;pos=pp(j,k);neg=(pp(i,j),pp(i,k));neigh=set()
 for e in neg:neigh.update(AB_pos.get(e,()))
 neigh.update(AB_neg.get(pos,()))
 # Independent comparison to all four source edge forms, including incoming forms.
 source=set()
 for l in adj[i]:
  for t in ((l,i,j),(l,i,k)):
   u=abid.get(t)
   if u is not None:source.add(u)
 for l in adj[j]:
  u=abid.get((l,j,i))
  if u is not None:source.add(u)
 for l in adj[k]:
  u=abid.get((l,k,i))
  if u is not None:source.add(u)
 for l in adj[k]:
  u=abid.get((j,k,l))
  if u is not None:source.add(u)
 for l in adj[j]:
  u=abid.get((k,j,l))
  if u is not None:source.add(u)
 for l in adj[j]&adj[k]:
  for t in ((j,l,k),(k,l,j)):
   u=abid.get(t)
   if u is not None:source.add(u)
 assert source==neigh
 source_c_edges+=len(source)
 max_neigh=max(max_neigh,len(neigh))
 c_neighborhood_hash.update(v.canonical([[i,j,k],sorted(neigh)])+b"\n")
 an=[u for u in neigh if u<len(A)];bn=[u for u in neigh if u>=len(A)]
 # Triangle C-A-B-C: same unique B-star component.
 a_by_comp={comp[u]:u for u in an}
 b_by_comp={comp[u]:u for u in bn}
 common=set(a_by_comp)&set(b_by_comp)
 if common:
  s=next(iter(common));star_witness=( (i,j,k), A[a_by_comp[s]], B[b_by_comp[s]-len(A)],s );break
 # 5-cycle C-A1-B1-B2-A2-C: A neighbors in both endpoint stars of a B-B quotient edge.
 acenters=set(comp[u] for u in an)
 for c1 in sorted(acenters):
  common_centers=bgraph.get(c1,set())&acenters
  if common_centers:
   c2=min(common_centers)
   five_witness=((i,j,k),c1,c2)
   break
 if five_witness:break
print('one-C scan',num_C,'max A/B neighbors per C',max_neigh,'triangle witness',star_witness,'five-cycle witness',five_witness,'seconds',round(time.monotonic()-t0,2),flush=True)

assert num_C==len(C)==70350 and star_witness is None and five_witness is None
assert max_neigh==556
# Actual R/R/P incidence explains the sparse high-weight interactions.
rn=collections.defaultdict(set)
for a,b in Rp:rn[a].add(b);rn[b].add(a)
rrp=collections.defaultdict(set);rrp_count=0
for a,b in P:
 for c in rn[a]&rn[b]:
  x=pp(a,c);y=pp(b,c);rrp[x].add(y);rrp[y].add(x);rrp_count+=1
assert rrp_count==68 and len(rrp)==136 and all(len(ns)==1 for ns in rrp.values())
rr_unit=sum(len(rn[a]&rn[b]) for a,b in E)
assert rr_unit==0

def conflict(u,w):
 i,j,k=u;l,a,b=w
 return pp(j,k) in {pp(l,a),pp(l,b)} or pp(a,b) in {pp(i,j),pp(i,k)}
def coefficient(triple):
 i,j,k=triple
 out=[0,0]
 for e,sign in [(pp(j,k),1),(pp(i,j),-1)]:
  assert e in U
  if e in P:out[0]+=sign
  elif e in Rp:out[1]+=sign
 return out
witnesses=[
 dict(name='three-P unit-triangle spokes',nodes=[(5535,877,4641),(7479,5535,4641),(877,7479,4641)],coefficients=[3,0],bound=1),
 dict(name='two-P one-R unit-triangle spokes',nodes=[(887,229,4641),(3483,887,4641),(229,3483,4641)],coefficients=[2,1],bound=1),
 dict(name='R-R-P transitivity edge',nodes=[(887,229,4641),(229,305,4641)],coefficients=[-1,2],bound=1),
]
for w in witnesses:
 ns=w['nodes'];cs=[coefficient(t) for t in ns]
 assert [sum(c[j] for c in cs) for j in range(2)]==w['coefficients']
 assert all(conflict(ns[i],ns[j]) for i in range(len(ns)) for j in range(i+1,len(ns)))
 w['nodes']=[list(t) for t in ns]
# Exact halfplane intersection for the asserted upper polygon.
hs=[(-F(1),F(0),F(0)),(F(0),-F(1),F(0)),(F(3),F(0),F(1)),(F(2),F(1),F(1)),(-F(1),F(2),F(1))]
vertices=set()
for i,(a,b,c) in enumerate(hs):
 for d,e,f in hs[i+1:]:
  det=a*e-d*b
  if not det:continue
  x=(c*e-f*b)/det;y=(a*f-d*c)/det
  if all(A*x+B*y<=C for A,B,C in hs):vertices.add((x,y))
expected={(F(0),F(0)),(F(1,3),F(0)),(F(1,3),F(1,3)),(F(1,5),F(3,5)),(F(0),F(1,2))}
assert vertices==expected
assert all(3*p<=1 and 2*p+r<=1 and 2*r-p<=1 for p,r in v.VERTICES)
report=dict(schema='known-node-bw-pr-odd-cycle-ceiling-v1',status='PASS_EXACT_ALL_LENGTH_RESTRICTED_FAMILY',
 geometry_semantic_sha256=v.GEOMETRY,P_basis_sha256=v.P_BASIS,R_basis_sha256=v.R_BASIS,
 node_classes=dict(A=len(A),B=len(B),C=len(C)),
 node_class_sha256={name:v.digest(nodes) for name,nodes in [('A',A),('B',B),('C',C)]},
 AB_edges=dict(AA=len(aa),AB=len(ab),BB=len(bb),total=len(ab_edges)),
 independent_source_edge_forms_equal=True,AB_edge_sha256=v.digest(sorted(ab_edges)),
 AB_components=dict(total=cid,B_centered=star_comps,isolated_A=isolated_A,largest=max(comp_sizes),max_B_per_component=max(comp_B.values()),max_B_neighbors_per_A=max(map(len,zadj[:len(A)]))),
 B_center_graph=dict(vertices=len(centers),edges=len(bb_edge_comps),loops=0,bipartite=True),
 C_scan=dict(nodes=num_C,max_AB_neighbors=max_neigh,source_edges=source_c_edges,independent_source_edge_forms_equal=True,forbidden_triangles=0,forbidden_five_cycles=0,neighborhood_sha256=c_neighborhood_hash.hexdigest()),
 RRP_interaction=dict(vertices=len(Rp),edges=rrp_count,nonisolated_vertices=len(rrp),maximum_degree=1,RR_unit_triangles=rr_unit),
 forcing_inequalities=witnesses,
 upper_polygon_vertices=[[str(p),str(r)] for p,r in sorted(vertices)],
 all_length_proof='Weighted A/B/C star lemma in the accompanying proof; not a bounded cycle-length enumeration.',
 scope='The induced BW auxiliary graph whose individual node expressions q_jk-q_ij use only known E/P/R pairs. All its edge and odd-cycle inequalities give exactly the displayed upper polygon, with p,r>=0. It covers simple 2-chorded cycles with all cycle/chord coordinates known. It does not cover unknown-coordinate nodes whose unknown terms cancel only after summation, full partition feasibility, or full15.')
path=ROOT/'certificates/bw_pr_odd_cycle_ceiling.json'
if args.write_receipt:path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
else:assert v.canonical(v.read(path))==v.canonical(report),'Saved receipt differs from exact replay'
print(json.dumps(report,sort_keys=True))
