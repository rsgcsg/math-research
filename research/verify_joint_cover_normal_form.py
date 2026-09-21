"""Finite calibration of T132's universal support/color-frame construction."""
from itertools import permutations
import json

def compose(a,b):return tuple(a[b[i]] for i in range(len(a)))
def inverse(a):return tuple(a.index(i) for i in range(len(a)))
def verify():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    k=3;r=2;m=2;palette=list(permutations(range(k)))
    words=[(0,1,0),(1,0,0)];g=(1,0,2);s=(1,0);p=[(0,1,2),(0,1,2)]
    base_sigma=(1,0);base_pi=[(1,2,0),(2,0,1)]
    states=[(a,b,lam) for a in range(r) for b in range(m) for lam in palette]
    word={i:tuple(i[2][c] for c in words[i[1]]) for i in states}
    old={};new={}
    for i in states:
        a,b,lam=i
        old[i]=(base_sigma[a],s[b],compose(compose(base_pi[a],lam),inverse(p[b])))
        new[i]=(a,s[b],compose(lam,inverse(p[b])))
        assert word[i][0]!=word[i][1]
        assert all(word[old[i]][g[x]]==base_pi[a][word[i][x]] for x in range(3))
        assert all(word[new[i]][g[x]]==word[i][x] for x in range(3))
        assert old[i][0]==base_sigma[a] and new[i][0]==a
    assert set(old.values())==set(states)==set(new.values())
    return dict(status='PASS',theorem='T132',states=len(states),points=3,
                old_and_new_domain_obligations=2*len(states)*3,
                scope='Finite calibration; arbitrary-size statement is proved in joint_cover_monodromy.md')
if __name__=='__main__':print(json.dumps(verify(),indent=2))
