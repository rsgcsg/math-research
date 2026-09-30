#!/usr/bin/env python3
"""Standard-library exact verification of the nine-point P/R projection certificate."""
import argparse,gzip,hashlib,json,sys
if not __debug__:
 raise RuntimeError("Verification requires assertions; run without -O")
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def canonical(x):
 return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def unique_keys(pairs):
 out={}
 for k,v in pairs:
  if k in out:raise ValueError('Duplicate JSON key '+k)
  out[k]=v
 return out
def readj(path):
 raw=path.read_bytes()
 if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
 return json.loads(raw,object_pairs_hook=unique_keys)
def rgs(n,k):
 out=[]
 def rec(a,m):
  if len(a)==n:out.append(tuple(a));return
  for x in range(min(m+2,k)):rec(a+[x],max(m,x))
 rec([0],0);return out
def intersect(L1,L2):
 a,b,c=L1;d,e,f=L2;det=a*e-d*b
 if det==0:return None
 return ((c*e-f*b)/det,(a*f-d*c)/det)
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--certificate',type=Path,default=ROOT/'certificates/nine_point_pr_polygon.json')
 ap.add_argument('--write-receipt',action='store_true')
 args=ap.parse_args()
 C=readj(args.certificate);h=C.pop('certificate_sha256')
 assert hashlib.sha256(canonical(C)).hexdigest()==h
 V=C['vertices'];U=C['seven_point_subset'];assert V==[4641,877,887,3483,5535,7479,7489,229,305]
 G=readj(ROOT/'certificates/Y_full_geometry.json.gz')
 PB=readj(ROOT/'certificates/g14_pair_orbit_basis.json.gz')
 RB=readj(ROOT/'certificates/g14_r_pair_orbit_basis.json.gz')
 Tcert=readj(ROOT/'certificates/g14_pr_transport_bound.json')
 from verify_pr_matching_window_ceiling import validate_inputs
 validate_inputs(G,PB,RB)
 tc=dict(Tcert);assert tc.pop('certificate_sha256')==hashlib.sha256(canonical(tc)).hexdigest()
 assert hashlib.sha256(canonical(G)).hexdigest()==C['geometry_semantic_sha256']
 assert C['geometry_semantic_sha256']==Tcert['geometry_semantic_sha256']==PB['geometry_semantic_sha256']==RB['geometry_semantic_sha256']
 assert C['P_component_sha256']==PB['basis_sha256']==Tcert['pair_components']['P']['basis_sha256']
 assert C['R_component_candidate_sha256']==RB['candidate_sha256']==Tcert['pair_components']['R']['candidate_sha256']
 Pnodes=set(map(tuple,PB['orbit_nodes_by_grade']['1/sqrt3']))
 Rnodes=set(map(tuple,RB['orbit_nodes']))
 Pforestnodes={tuple(sorted(x)) for e in PB['forest_edges'] if e.get('grade')=='1/sqrt3' for x in (e['source'],e['target'])}
 Rforestnodes={tuple(sorted(x)) for e in RB['forest_edges'] for x in (e['source'],e['target'])}
 assert Pforestnodes==Pnodes and Rforestnodes==Rnodes
 assert len(Pnodes)==1860 and len(Rnodes)==1472 and sum(e.get('grade')=='1/sqrt3' for e in PB['forest_edges'])==1859 and sum(e.get('grade')=='2' for e in PB['forest_edges'])==779
 # Recompute exact squared distances for every local pair in the certified 32-dimensional basis.
 from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice
 def squared_distance(a,b,points,den,table):
  d=[x-y for x,y in zip(points[a],points[b])]
  return tuple(F(x,4*den*den) for x in product_twice(d,conjugate_twice(d),table))
 table=multiplication_twice();pts=G['points'];den=G['denominator']
 def d2(a,b):return squared_distance(a,b,pts,den,table)
 unit=(F(1),)+(F(0),)*31;pd=(F(1,3),)+(F(0),)*31;rd=(F(4,3),)+(F(0),)*31
 ids={v:i for i,v in enumerate(V)}
 localpairs=list(combinations(V,2));dist={tuple(sorted(e)):d2(*e) for e in localpairs}
 globaledges={tuple(sorted(e)) for e in G['edges']}
 units=sorted(tuple(sorted(e)) for e in localpairs if dist[tuple(sorted(e))]==unit)
 assert units==sorted(tuple(sorted(e)) for e in C['induced_unit_edges'])
 assert all((tuple(sorted(e)) in globaledges)==(dist[tuple(sorted(e))]==unit) for e in localpairs)
 pe=sorted(tuple(sorted(e)) for e in localpairs if tuple(sorted(e)) in Pnodes)
 re=sorted(tuple(sorted(e)) for e in localpairs if tuple(sorted(e)) in Rnodes)
 assert [list(e) for e in pe]==C['P_events'] and [list(e) for e in re]==C['R_events']
 assert len(pe)==14 and len(re)==5 and (229,877) in pe
 assert all(dist[e]==pd for e in pe) and all(dist[e]==rd for e in re)
 # Record all same-distance pairs and component membership: do not use distance alone to select event rows.
 same_p=sorted(tuple(sorted(e)) for e in localpairs if dist[tuple(sorted(e))]==pd)
 same_r=sorted(tuple(sorted(e)) for e in localpairs if dist[tuple(sorted(e))]==rd)
 assert set(pe)==set(same_p) and set(re)==set(same_r)
 assert (229,877) in pe and len(same_p)==14
 assert len(same_r)==5
 # Independently enumerate every unlabeled partition into <=5 blocks, then all locally proper ones.
 allparts=rgs(len(V),5);unitidx=[(ids[a],ids[b]) for a,b in units]
 proper=[z for z in allparts if all(z[a]!=z[b] for a,b in unitidx)]
 assert len(allparts)==18002 and len(proper)==2277
 assert Counter(max(z)+1 for z in proper)=={3:54,4:714,5:1509}
 peidx=[(ids[a],ids[b]) for a,b in pe];reidx=[(ids[a],ids[b]) for a,b in re]
 uidx=[ids[v] for v in U]
 def same(z,pair):return int(z[pair[0]]==z[pair[1]])
 # The seven-point core has exactly 12 P and 3 R component rows; the triangle has two R rows and its P base.
 coreP=sorted(tuple(sorted((a,b))) for a,b in combinations(U,2) if tuple(sorted((a,b))) in Pnodes)
 coreR=sorted(tuple(sorted((a,b))) for a,b in combinations(U,2) if tuple(sorted((a,b))) in Rnodes)
 assert len(coreP)==12 and len(coreR)==3
 pextra=(229,305);r1=(229,4641);r2=(305,4641)
 assert pextra in pe and r1 in re and r2 in re
 # Pointwise dual/face inequalities are checked on every locally proper partition.
 lower_scores=[];core_counts=[];tri_scores=[]
 upperp=( (4641,877),(4641,5535),(4641,7479) )
 mixspokes=((4641,887),(4641,3483),(4641,229))
 assert all(tuple(sorted(x)) in set(pe) for x in upperp+mixspokes[:2])
 assert tuple(sorted(mixspokes[2])) in set(re)
 for z in proper:
  N=sum(same(z,(ids[a],ids[b])) for a,b in coreP+coreR)
  T=same(z,(ids[r1[0]],ids[r1[1]]))+same(z,(ids[r2[0]],ids[r2[1]]))-same(z,(ids[pextra[0]],ids[pextra[1]]))
  assert N>=2 and T<=1
  score=1-2*N+3*T
  assert score<=0
  lower_scores.append(score);core_counts.append(N);tri_scores.append(T)
  assert sum(same(z,(ids[a],ids[b])) for a,b in upperp)<=1
  assert sum(same(z,(ids[a],ids[b])) for a,b in mixspokes)<=1
  assert T<=1
 # Verify every rational primal support law against all 14+5 individual row equalities.
 expected_vertices={}
 for v in C['vertices_of_projected_polytope']:
  p=F(v['p']);r=F(v['r']); weights=[];mP=[F(0) for _ in pe];mR=[F(0) for _ in re]
  for term in v['support']:
   z=tuple(term['partition']);w=F(term['weight']);assert len(z)==9 and w>0 and z in allparts
   assert all(type(x) is int and 0<=x<5 for x in z)
   assert all(z[a]!=z[b] for a,b in unitidx)
   weights.append(w)
   for j,edge in enumerate(peidx):mP[j]+=w*same(z,edge)
   for j,edge in enumerate(reidx):mR[j]+=w*same(z,edge)
  assert sum(weights)==1,(p,r,sum(weights))
  if p==F(1,27):
   for term in v['support']:
    z=tuple(term['partition'])
    N=sum(same(z,(ids[a],ids[b])) for a,b in coreP+coreR)
    T=same(z,(ids[r1[0]],ids[r1[1]]))+same(z,(ids[r2[0]],ids[r2[1]]))-same(z,(ids[pextra[0]],ids[pextra[1]]))
    assert N==2 and T==1
  assert all(x==p for x in mP),(p,r,mP)
  assert all(x==r for x in mR),(p,r,mR)
  assert (p,r) not in expected_vertices
  expected_vertices[(p,r)]=len(weights)
 ref={ (F(p),F(r)) for p,r in C['reference_polygon_vertices'] }
 assert set(expected_vertices)==ref
 # The exact intersection of five valid halfplanes (plus p>=0) has exactly the listed pentagon vertices.
 hs=[(-F(4),-F(1),-F(2,3)),(F(0),-F(1),F(0)),(F(1),F(0),F(1,3)),(F(2),F(1),F(1)),(-F(1),F(2),F(1)),(-F(1),F(0),F(0))]
 intersections=set()
 for x,y in combinations(hs,2):
  z=intersect(x,y)
  if z and all(a*z[0]+b*z[1]<=c for a,b,c in hs):intersections.add(z)
 assert intersections==ref,(intersections,ref)
 # Every vertex is feasible; every local law obeys the halfplanes, so projection is precisely this polygon.
 assert max(lower_scores)==0
 report={'status':'PASS_EXACT_LOCAL_NINE_POINT_PR_POLYGON','certificate_sha256':h,'geometry_semantic_sha256':C['geometry_semantic_sha256'],
  'P_component_nodes':len(Pnodes),'R_component_nodes':len(Rnodes),'local_pair_membership_checked_against_forest':True,'P_event_rows':len(pe),'R_event_rows':len(re),
  'unit_edges':len(units),'all_partitions_at_most5':len(allparts),'locally_proper_partitions':len(proper),
  'distinct_event_signatures':len({tuple(same(z,e) for e in peidx+reidx) for z in proper}),
  'same_distance_pairs_not_in_P_component':sorted(set(same_p)-set(pe)),'same_distance_pairs_not_in_R_component':sorted(set(same_r)-set(re)),
  'pointwise_lower_dual_scores_min_max':[str(min(lower_scores)),str(max(lower_scores))],
  'lower_optimum_support_all_has_N7_2_and_T_1':True,
  'tight_seven_count_states':sum(x==2 for x in core_counts),'tight_triangle_transitivity_states':sum(x==1 for x in tri_scores),
  'exact_vertices':[[str(p),str(r),expected_vertices[(p,r)]] for p,r in sorted(expected_vertices)],
  'facets':['12p+3r>=2','r>=0','p<=1/3','2p+r<=1','2r-p<=1'],
  'scope':C['scope']}
 receipt=ROOT/'certificates/nine_point_pr_polygon_verification.json'
 if args.write_receipt:receipt.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 else:assert canonical(readj(receipt))==canonical(report),'Saved receipt differs from exact replay'
 print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
