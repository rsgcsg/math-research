"""Export complete background-color contact matrices and movable sites."""
import json
import hashlib
from finite_background_repair import prepare, ROOT


def build():
    core,words,cross,equal,neighbors,bg,patch=prepare()
    witnesses=[]
    for a in range(5):
        for b in range(5):
            for name,relation in (('unit',cross),('equal',equal)):
                left,right=next((u,v) for u,v in sorted(relation)
                                if u[0]==-1 and v[0]==1 and bg(u)==a and bg(v)==b)
                witnesses.append(dict(old_colors=[a,b],relation=name,endpoints=[left,right]))
    movable=[]
    for sign in (-1,1):
        for c in range(5):
            for q in range(509):
                v=(sign,0,0,q)
                if bg(v)!=c:continue
                free=set(range(5))-{bg(w) for w in neighbors(v)}-{c}
                if free:
                    movable.append(dict(vertex=v,old=c,new=min(free)));break
            else:raise AssertionError('No movable witness')
    return dict(schema=1,background_words=words,witnesses=witnesses,movable=movable,
                input_sha256={name:hashlib.sha256((ROOT/'certificates'/name).read_bytes()).hexdigest()
                              for name in ('parts509_core.json','multicenter_cores.json')},
                scope='Specified T059 words with m-mod3 offsets only; neither array background is frozen')


if __name__=='__main__':
    result=build()
    (ROOT/'certificates/palette_activation_obstruction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('50 geometric witnesses and 10 one-site moves exported')
