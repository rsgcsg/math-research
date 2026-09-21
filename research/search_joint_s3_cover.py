"""E102 search-side reproduction using an optional system libz3 (4.13.3 here).

No pip installation is required when libz3 is available. Otherwise this script
fails with a dependency error; the independent standard-library verifier still
works. Solver failures are search observations, never proof certificates.
Output is separate from the canonical independently verified certificate.
"""
import ctypes as C,ctypes.util,time,json,re
P=C.c_void_p; U=C.c_uint; S=C.c_char_p
lib=C.CDLL(ctypes.util.find_library('z3'))
def bind(n,r,*a):
 f=getattr(lib,'Z3_'+n);f.restype=r;f.argtypes=list(a);return f
mk_config=bind('mk_config',P);del_config=bind('del_config',None,P)
mk_context=bind('mk_context',P,P);del_context=bind('del_context',None,P)
mk_string_symbol=bind('mk_string_symbol',P,P,S)
mk_tactic=bind('mk_tactic',P,P,S);tactic_inc_ref=bind('tactic_inc_ref',None,P,P)
mk_solver_from_tactic=bind('mk_solver_from_tactic',P,P,P)
mk_solver_for_logic=bind('mk_solver_for_logic',P,P,P)
solver_inc_ref=bind('solver_inc_ref',None,P,P)
solver_from_string=bind('solver_from_string',None,P,P,S)
solver_check=bind('solver_check',C.c_int,P,P)
solver_get_model=bind('solver_get_model',P,P,P)
model_to_string=bind('model_to_string',S,P,P)
model_inc_ref=bind('model_inc_ref',None,P,P)
solver_get_reason_unknown=bind('solver_get_reason_unknown',S,P,P)
solver_get_statistics=bind('solver_get_statistics',P,P,P)
stats_to_string=bind('stats_to_string',S,P,P)
mk_params=bind('mk_params',P,P);params_inc_ref=bind('params_inc_ref',None,P,P)
params_set_uint=bind('params_set_uint',None,P,P,P,U)
solver_set_params=bind('solver_set_params',None,P,P,P)
solver_get_help=bind('solver_get_help',S,P,P)
get_full_version=bind('get_full_version',S)

def solve(text,seconds=60,conflicts=100000,out=None):
 cfg=mk_config();ctx=mk_context(cfg);del_config(cfg)
 sol=mk_solver_for_logic(ctx,mk_string_symbol(ctx,b'QF_FD'));solver_inc_ref(ctx,sol)
 pars=mk_params(ctx);params_inc_ref(ctx,pars)
 params_set_uint(ctx,pars,mk_string_symbol(ctx,b'timeout'),int(seconds*1000))
 params_set_uint(ctx,pars,mk_string_symbol(ctx,b'max_conflicts'),conflicts)
 solver_set_params(ctx,sol,pars)
 t=time.time();solver_from_string(ctx,sol,text.encode());loaded=time.time()-t
 print('Z3_LOADED',len(text),round(loaded,3),get_full_version().decode(),flush=True)
 ans=solver_check(ctx,sol);dt=time.time()-t
 result=dict(status={1:'SAT',-1:'UNSAT_SEARCH_ONLY',0:'UNKNOWN'}[ans],seconds=dt,load_seconds=loaded,version=get_full_version().decode())
 if ans==1:
  model=solver_get_model(ctx,sol);model_inc_ref(ctx,model);result['model']=model_to_string(ctx,model).decode()
 elif ans==0:result['reason']=solver_get_reason_unknown(ctx,sol).decode()
 result['stats']=stats_to_string(ctx,solver_get_statistics(ctx,sol)).decode()
 if out:open(out,'w').write(json.dumps(result,indent=2))
 print('Z3_RESULT',json.dumps({k:v for k,v in result.items() if k!='model'}),flush=True)
 del_context(ctx);return result

from pathlib import Path
from dyadic_mixed_return_joint import prepare
from quintic_multiword_joint import MultiwordEncoding


def run(root, with_u=False, seconds=100, conflicts=200000):
    report,context,source,_,_,definitions,maps=prepare(root)
    old=source['result'];n=len(context['points']);m=15
    signs=[-1 if j in (4,13) else 1 for j in range(14)]
    shifts=[[1]*5,[1]*5,[0]*5,[2]*5,[1]*5,[0]*5,[0]*5,[2,0,0,0,1],
            [0]*5,[0]*5,[0]*5,[0]*5,[0]*5,[1]*5]
    sigma=[];palettes=[]
    for j in range(14):
        sigma.append([3*old['word_permutations'][j][a]+(signs[j]*s+shifts[j][a])%3
                      for a in range(5) for s in range(3)])
        palettes.append([old['color_permutations'][j][a] for a in range(5) for s in range(3)])
    parent=list(range(n*m*5));size=[1]*len(parent)
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def join(x,y):
        x,y=find(x),find(y)
        if x==y:return
        if size[x]<size[y]:x,y=y,x
        parent[y]=x;size[x]+=size[y]
    for j,mapping in enumerate(maps[:14]):
        for a in range(m):
            for p,q in mapping:
                for c in range(5):join((a*n+p)*5+c,(sigma[j][a]*n+q)*5+palettes[j][a][c])
    roots=[find(i) for i in range(len(parent))]
    labels={r:i+1 for i,r in enumerate(sorted(set(roots)))}
    classes=[labels[r] for r in roots];clauses=set()
    def color(a,p,c):return classes[(a*n+p)*5+c]
    for a in range(m):
        for p in range(n):
            cs=[color(a,p,c) for c in range(5)];clauses.add(tuple(sorted(set(cs))))
            for i in range(5):
                for j in range(i):clauses.add(tuple(sorted({-cs[i],-cs[j]})))
        for p,q in context['edges']:
            for c in range(5):clauses.add(tuple(sorted({-color(a,p,c),-color(a,q,c)})))
    class Encoding(MultiwordEncoding):
        def color(self,a,p,c):return color(a,p,c)
    enc=Encoding.__new__(Encoding);enc.n=n;enc.m=m;enc.k=5;enc.top=len(labels);enc.witness_vars=[]
    clauses=list(sorted(clauses))
    if with_u:clauses.extend(enc.add_motion(maps[14]))
    else:clauses.append([-color(0,31,1)])  # obtain a genuinely new old14 word family
    lines=[f'(declare-const v{i} Bool)' for i in range(1,enc.top+1)]
    for clause in clauses:
        literals=[f'v{x}' if x>0 else f'(not v{-x})' for x in clause]
        lines.append('(assert '+(' '.join(['(or']+literals)+')' if len(literals)>1 else literals[0])+')')
    answer=solve('\n'.join(lines),seconds=seconds,conflicts=conflicts)
    result=None
    if answer['status']=='SAT':
        positive=[int(x) for x in re.findall(r'v(\d+) -> true',answer['model'])]
        result=enc.decode(positive)
        result['word_permutations']=sigma+result['word_permutations']
        result['color_permutations']=palettes+result['color_permutations']
        result['motions']=[d[0] for d in definitions[:15 if with_u else 14]]
    answer.pop('model',None)
    return dict(experiment='E102',geometry=report['geometry'],signs=signs,shifts=shifts,
                support=m,with_u=with_u,search=answer,result=result,
                scope='Search only. Independently verify positive words; UNSAT here is not an all-cover obstruction.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--with-u',action='store_true')
    parser.add_argument('--seconds',type=int,default=100);parser.add_argument('--conflicts',type=int,default=200000)
    parser.add_argument('--output',required=True);args=parser.parse_args()
    if args.seconds<1 or args.conflicts<1:parser.error('Search limits must be positive')
    result=run(Path(__file__).resolve().parents[1],args.with_u,args.seconds,args.conflicts)
    Path(args.output).write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='result'},indent=2))
