"""Exact positive checker: all old module obligations AND full nu domain.

No search imports. A negative/unknown sufficient-model search is not accepted.
"""
from fractions import Fraction as Q
from pathlib import Path
import json
from verify_quintic_three_character_law import verify as predecessor


def verify(root, certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    certificate=certificate or root/'certificates/quintic_nu_joint_law.json'
    data=json.loads(certificate.read_text())
    report,context=predecessor(root,certificate,expected_experiment='E072',geometry_context=True)
    points=context['physical'];mul=context['mul']
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    assert mul(nu,context['bar'](nu))==context['one']
    lookup={p:i for i,p in enumerate(points)}
    domain=[]
    for i,p in enumerate(points):
        q=mul(nu,p)
        if q in lookup:domain.append([i,lookup[q]])
    assert domain==data['nu_domain'] and len(domain)==271
    sigma=data['word_permutation'];perms=data['color_permutations'];words=data['result']['words']
    assert sorted(sigma)==list(range(3)) and len(perms)==3
    assert all(sorted(pi)==list(range(5)) for pi in perms)
    assert all(int(words[j][v])==perms[j][int(words[sigma[j]][u])]
               for u,v in domain for j in range(3))
    return dict(status='PASS',experiment='E072',geometry=report['geometry'],
                proper_words=3,nu_domain=len(domain),word_permutation=sigma,color_permutations=perms,
                scope='One common full-joint law for all old module motions and nu maximal domain; not every maximal domain of the generated group')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
