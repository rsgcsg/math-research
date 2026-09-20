"""E099: full-joint CEGAR using T127's exact quadratic moments.

All five words remain free; no support/action permutation is guessed by SAT.
The finite support size is a restriction: UNKNOWN/UNSAT is not an HN result.
"""
from collections import Counter, defaultdict, deque
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import argparse
import hashlib
import json
import time
from verify_finite_joint_compression import partition_witness


def shape(values):
    labels={}
    return tuple(labels.setdefault(x,len(labels)) for x in values)


def separating_events(left, right, limit=3):
    """Five equally weighted <=5-block words: return true quadratic mismatches.

T114 finds <=6 candidate physical positions. T127 guarantees a degree<=2
positive-equality monomial on them. The returned counts are checked directly.
"""
    assert len(left)==len(right)==5
    signed=Counter(left);signed.subtract(right)
    signed={p:w for p,w in signed.items() if w}
    if not signed:return []
    predicates,mass=partition_witness(signed)
    assert mass and len(predicates)<=3
    ids=sorted({i for i,j,b in predicates}|{j for i,j,b in predicates})
    pairs=list(combinations(ids,2))
    columns=[[int(p[i]==p[j]) for p in left+right] for i,j in pairs]
    candidates=[]
    for a,b in combinations_with_replacement(range(len(pairs)),2):
        values=[x*y for x,y in zip(columns[a],columns[b])]
        counts=[sum(values[:5]),sum(values[5:])]
        if counts[0]!=counts[1]:
            event=tuple(sorted({pairs[a],pairs[b]}))
            candidates.append((-abs(counts[0]-counts[1]),event,counts))
    assert candidates, 'T127 would be contradicted; retain the failing words'
    candidates.sort()
    return [(event,counts) for _,event,counts in candidates[:limit]]


class Encoding:
    def __init__(self,n,edges):
        self.n=n;self.top=n*25;self.eq={};self.events={};self.cuts=set();self.clauses=[]
        for a in range(5):
            for i in range(n):
                vs=[self.color(a,i,c) for c in range(5)]
                self.clauses.append(vs)
                self.clauses.extend([[-v,-w] for v,w in combinations(vs,2)])
            self.clauses.extend([[-self.color(a,i,c),-self.color(a,j,c)] for i,j in edges for c in range(5)])

    def color(self,a,i,c):return (a*self.n+i)*5+c+1

    def fresh(self):self.top+=1;return self.top

    def equality(self,a,i,j,clauses):
        i,j=sorted((i,j));key=(a,i,j)
        if key not in self.eq:
            e=self.fresh();self.eq[key]=e
            if i==j:clauses.append([e])
            else:
                for c in range(5):
                    x,y=self.color(a,i,c),self.color(a,j,c)
                    clauses.extend([[-x,-y,e],[-e,-x,y]])
        return self.eq[key]

    def event(self,a,pairs,clauses):
        pairs=tuple(sorted(set(tuple(sorted(p)) for p in pairs)));key=(a,pairs)
        if key not in self.events:
            vs=[self.equality(a,i,j,clauses) for i,j in pairs]
            if len(vs)==1:e=vs[0]
            else:
                assert len(vs)==2
                e=self.fresh();clauses.extend([[-e,v] for v in vs]);clauses.append([e]+[-v for v in vs])
            self.events[key]=e
        return self.events[key]

    def add_event(self,t,event,mapping):
        from pysat.card import CardEnc, EncType
        key=(t,event);assert key not in self.cuts;self.cuts.add(key)
        clauses=[]
        source=[(mapping[i][0],mapping[j][0]) for i,j in event]
        image=[(mapping[i][1],mapping[j][1]) for i,j in event]
        literals=[self.event(a,source,clauses) for a in range(5)]
        literals += [-self.event(a,image,clauses) for a in range(5)]
        # Remove exact complementary occurrences; they contribute constant one.
        multiplicities=Counter(literals);bound=5
        for v in {abs(x) for x in literals}:
            z=min(multiplicities[v],multiplicities[-v]);bound-=z
            multiplicities[v]-=z;multiplicities[-v]-=z
        literals=[lit for lit,count in multiplicities.items() for _ in range(count)]
        if literals:
            cnf=CardEnc.equals(lits=literals,bound=bound,top_id=self.top,encoding=EncType.seqcounter)
            self.top=max(self.top,cnf.nv);clauses.extend(cnf.clauses)
        else:assert bound==0
        return clauses

    def words(self,model):
        positive={v for v in model if v>0}
        return [''.join(str(next(c for c in range(5) if self.color(a,i,c) in positive))
                        for i in range(self.n)) for a in range(5)]


def decode_law(words,mappings):
    sigmas=[];palettes=[]
    for mapping in mappings:
        targets=defaultdict(deque)
        for b,w in enumerate(words):targets[shape(w[j] for i,j in mapping)].append(b)
        sigma=[];pp=[]
        for a,w in enumerate(words):
            b=targets[shape(w[i] for i,j in mapping)].popleft();sigma.append(b)
            relation={}
            for i,j in mapping:
                x,y=int(w[i]),int(words[b][j])
                if x in relation:assert relation[x]==y
                relation[x]=y
            assert len(set(relation.values()))==len(relation)
            rest=iter(sorted(set(range(5))-set(relation.values())))
            pp.append([relation[x] if x in relation else next(rest) for x in range(5)])
        assert sorted(sigma)==list(range(5));sigmas.append(sigma);palettes.append(pp)
    return dict(words=words,word_permutations=sigmas,color_permutations=palettes,
                full_domain_count=len(mappings))


def run(root,budget=300000,rounds=250,seconds=600):
    from pysat.solvers import Solver
    from dyadic_mixed_return_joint import prepare
    parent,c,old,algebra,mapping,definitions,maps=prepare(root)
    one,eta,z,u,bar,mul=algebra
    definitions.insert(15,('dyadic_u_squared',mul(u,u),tuple(0 for _ in one),False))
    maps.insert(15,mapping(mul(u,u)))
    assert len(maps)==17 and list(map(len,maps[-3:]))==[29,805,33]
    enc=Encoding(len(c['points']),c['edges']);lookup={p:i for i,p in enumerate(c['points'])}
    for a in range(5):
        for color,j in enumerate((0,153,150)):
            enc.clauses.append([enc.color(a,lookup[c['ring']['blocks'][0][j]],color)])
    history=[];status='UNKNOWN';result=None;checkpoints=[];active=15
    words=old['result']['words'];start=time.monotonic()
    with Solver(name='cadical195',bootstrap_with=enc.clauses) as solver:
        del enc.clauses
        solver.set_phases([enc.color(a,i,int(color)) for a,w in enumerate(words) for i,color in enumerate(w)])
        for step in range(rounds):
            cuts=[]
            if words is not None:
                for t,mm in enumerate(maps[:active]):
                    left=[shape(w[i] for i,j in mm) for w in words]
                    right=[shape(w[j] for i,j in mm) for w in words]
                    for event,counts in separating_events(left,right):
                        cuts.append((t,event,counts))
                if not cuts:
                    result=decode_law(words,maps[:active]);result['motions']=[d[0] for d in definitions[:active]]
                    result['mapping_sha256']=[hashlib.sha256(json.dumps(mm,separators=(',',':')).encode()).hexdigest() for mm in maps[:active]]
                    checkpoints.append(dict(domains=active,round=step))
                    print('CHECKPOINT '+json.dumps(checkpoints[-1]),flush=True)
                    if active==17:status='SAT';break
                    active+=1;continue
                for t,event,counts in cuts:solver.append_formula(enc.add_event(t,event,maps[t]))
            stats=solver.accum_stats()
            entry=dict(round=step,active_domains=active,new_events=len(cuts),
                       events=len(enc.cuts),variables=enc.top,conflicts=stats['conflicts'])
            history.append(entry);print('MOMENT '+json.dumps(entry),flush=True)
            remaining=budget-stats['conflicts']
            if remaining<=0 or time.monotonic()-start>=seconds:break
            solver.conf_budget(min(10000,remaining));answer=solver.solve_limited()
            words=enc.words(solver.get_model()) if answer is True else None
            if answer is False:status='UNSAT_FIXED_SUPPORT_UNCERTIFIED';break
        stats=solver.accum_stats()
    data=dict(schema=1,experiment='E099',support=5,colors=5,geometry=parent['geometry'],
              result=result,search=dict(status=status,checkpoints=checkpoints,history=history,
              stats=stats,events=len(enc.cuts),variables=enc.top,
              elapsed_seconds=round(time.monotonic()-start,3)),
              scope='T127 quadratic counts exactly enforce each chosen equal-weight-five full law; no all-support or HN negative claim')
    (root/'certificates/joint_moment_cegar.json').write_text(json.dumps(data,indent=2)+'\n')
    print('SEARCH_SUMMARY '+json.dumps({k:v for k,v in data['search'].items() if k!='history'}),flush=True)
    return data


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--budget',type=int,default=300000)
    ap.add_argument('--rounds',type=int,default=250);ap.add_argument('--seconds',type=int,default=600)
    args=ap.parse_args();run(Path(__file__).resolve().parents[1],args.budget,args.rounds,args.seconds)
