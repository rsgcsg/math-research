"""Exhaustive small semantic tests of producer and separately rebuilt pricing CNFs."""
from itertools import product
import json
import random
from event_pricing_cnf import formula
from verify_event_pricing import rebuild, score, partition_value


def checks():
    if not __debug__: raise RuntimeError('verification requires assertions')
    rng=random.Random(20260927);assignments=flips=0;biggest=0
    for trial in range(96):
        n=4;k=3;events=[]
        for j in range(3):
            if trial%2:
                length=(trial+j)%5
                source=rng.sample(range(n),length);target=rng.sample(range(n),length)
                labels={};pattern=[labels.setdefault(x,len(labels)) for x in rng.choices(range(k),k=length)]
                events.append(dict(source=source,target=target,pattern=pattern))
            else: events.append(rng.choices(range(n),k=4))
        coefficients=[rng.randrange(-5,6) for _ in events];target=rng.randrange(-10,11)
        if trial>=94:coefficients=[10**12,-10**12,2**70];target=2**69
        edges=[[0,1],[2,3]]
        a=formula(n,edges,k,events,coefficients,target);b=rebuild(n,edges,k,events,coefficients,target)
        assert a['clauses']==b['clauses'] and a['cnf_sha256']==b['cnf_sha256']
        biggest=max(biggest,a['nv'])
        for word in product(range(k),repeat=n):
            values={i*k+c+1:word[i]==c for i in range(n) for c in range(k)}
            values[a['false']]=False
            for (x,y),v in a['equality'].items():values[v]=word[x]==word[y]
            for (ids,pattern),v in a['partitions'].items():values[v]=partition_value(word,ids,pattern)
            def bit(lit):return values[abs(lit)]==(lit>0)
            for op,x,y,z in a['gates']:
                xx,yy=bit(x),bit(y)
                values[z]=(xx and yy) if op=='and' else (xx or yy) if op=='or' else xx!=yy
            assert len(values)==a['nv']
            accepted=all(any(bit(lit) for lit in clause) for clause in a['clauses'])
            assert accepted==(all(word[x]!=word[y] for x,y in edges) and score(word,events,coefficients)<=target)
            assignments+=1
            if accepted and trial<16:
                for v in range(n*k+1,a['nv']+1):
                    values[v]=not values[v]
                    assert not all(any(bit(lit) for lit in clause) for clause in a['clauses'])
                    values[v]=not values[v];flips+=1
    return dict(status='PASS',queries=96,complete_color_assignments=assignments,
                auxiliary_single_bit_rejections=flips,max_variables=biggest,
                integer_coefficient_bits=71,scope='Finite semantic calibration, supplemented by the general written encoding proof.')


if __name__=='__main__':print(json.dumps(checks(),indent=2))
