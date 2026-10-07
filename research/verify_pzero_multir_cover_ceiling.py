#!/usr/bin/env python3
"""Independent exact replay of T175's P=0 multi-R-complement cover ceiling."""
import json
from fractions import Fraction as F
from pathlib import Path

from check_transport_projection import read, require, verify_geometry_and_components
from verify_q_defect_lifting import geometry
from verify_q_joint_boundary_gap import boundary_problem

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'certificates/q_joint_boundary_gap.json'
CERT=ROOT/'certificates/pzero_multir_cover_ceiling.json'

def check_word(word,b,local,P,Qpair,R):
    order=b['order']; require(len(word)==len(order),'word length')
    require(all(type(x) is int and 0<=x<5 for x in word),'five colors')
    c=dict(zip(order,word))
    require(all(c[a]!=c[d] for a,d in local['E']),'proper actual unit graph')
    require(all(c[a]!=c[d] for a,d in P),'all P zero')
    require(c[Qpair[0]]==c[Qpair[1]],'named Q is one')
    for w in b['saturated_windows']:
        equal=sum(c[a]==c[d] for i,a in enumerate(w) for d in w[i+1:])
        require(equal==2,'saturated seven-point window')
    a,o,d=b['PRR_triple']
    require((c[a]==c[o])+(c[d]==c[o])-(c[a]==c[d])==1,'PRR equality')
    return [int(c[a]!=c[d]) for a,d in R]

def main():
    source=read(SOURCE); cert=read(CERT); b=source['boundary']
    g=read(ROOT/'certificates/Y_full_geometry.json.gz')
    pb=read(ROOT/'certificates/g14_pair_orbit_basis.json.gz')
    rb=read(ROOT/'certificates/g14_r_pair_orbit_basis.json.gz')
    _,sets,_=verify_geometry_and_components(g,pb,rb)
    local=geometry(g,sets,b['vertices'])
    boundary_problem(b,local)
    terms=b['terms']
    P=[tuple(t['pair']) for t in terms if t['type']=='P']
    Q=[tuple(t['pair']) for t in terms if t['type']=='Q']
    R=[tuple(t['pair']) for t in terms if t['type']=='R']
    require((len(P),len(Q),len(R))==(47,11,31),'event counts')
    require(cert['event_counts']=={'P':47,'Q':11,'R':31},'certificate counts')
    require(cert['cover_mass']==2 and len(cert['dual_Q_rows'])==11,'mass and rows')
    prrP=(229,305); r1=(229,4641); r2=(305,4641)
    require(tuple(b['PRR_triple'])==(229,4641,305),'fixed PRR triple')
    require(prrP in P and r1 in R and r2 in R,'typed PRR events')
    require(cert['upper_cover_R_pairs']==[list(r1),list(r2)],'stored upper cover')
    seen_q=set()
    for row in cert['dual_Q_rows']:
        q=tuple(row['Q_pair']); require(q in Q and q not in seen_q,'Q identity')
        seen_q.add(q)
        za=check_word(row['witness_A'],b,local,P,q,R)
        zb=check_word(row['witness_B'],b,local,P,q,R)
        require(all(not (a and d) for a,d in zip(za,zb)),
                'dual R-complement supports disjoint')
    require(seen_q==set(Q),'all Q identities')
    require(2*(1-F(14,27))==F(26,27)>F(7,10),'C030 ceiling arithmetic')
    print(json.dumps({'status':'PASS','research_id':'T175','Q_rows':11,
                      'cover_mass':2,'C030_min_cover_cost':'26/27'},sort_keys=True))

if __name__=='__main__': main()
