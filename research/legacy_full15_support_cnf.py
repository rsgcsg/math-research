"""Standard-library semantic encoding of finite-support full-domain queries.

Uniform state matching and weighted (2,1,1) splitting are different models.
Eta-only color normalization is justified in the accompanying proof. Nothing
here supplies a bound on the support of an arbitrary feasible joint law.
"""
from array import array
from hashlib import sha256
from itertools import combinations

SPLIT_TYPES = (((0,0),(1,1),(2,2)), ((0,0),(1,2),(2,1)),
               ((0,1),(0,2),(1,0),(2,0)))
UNIFORM_CASES = ((0,1,2),(1,0,2),(1,2,0))

def require(ok, message):
    if not ok: raise ValueError(message)

class PackedClauses:
    """Store large CNFs without millions of separate Python lists."""
    def __init__(self):
        self.literals=array('i'); self.ends=array('Q',[0])
    def append(self,c):
        self.literals.extend(c); self.ends.append(len(self.literals))
    def __len__(self): return len(self.ends)-1
    def __getitem__(self,i):
        if not 0<=i<len(self): raise IndexError(i)
        return list(self.literals[self.ends[i]:self.ends[i+1]])
    def __iter__(self):
        for i in range(len(self)): yield self[i]
    def lines(self,nv):
        yield f'p cnf {nv} {len(self)}\n'
        for c in self: yield ' '.join(map(str,c))+' 0\n'
    def digest(self,nv):
        h=sha256()
        for s in self.lines(nv): h.update(s.encode())
        return h.hexdigest()
    def dimacs(self,nv,path):
        with open(path,'w') as f: f.writelines(self.lines(nv))


def build(data, eta_edges, m=3, kind='uniform', symmetry=True, k=5, eta=2):
    require(type(m) is int and m>0 and type(k) is int and k>0,'size')
    require(kind in ('uniform','211') and (kind!='211' or m==3),'weight model')
    require(all(type(a) is int and type(b) is int and 0<=a<m and 0<=b<m
                for a,b in eta_edges),'eta state edges')
    if kind=='uniform':
        require(sorted(a for a,b in eta_edges)==list(range(m))
                and sorted(b for a,b in eta_edges)==list(range(m)), 'eta permutation')
    else: require(tuple(map(tuple,eta_edges)) in SPLIT_TYPES,'eta weighted case')
    n=len(data['points']); graph=[[] for _ in range(m*n)]
    for i,j in eta_edges:
        for a,b in data['mappings'][eta]:
            x=i*n+a; y=j*n+b; graph[x].append(y);graph[y].append(x)
    comp=[-1]*(m*n); count=0
    for x in range(m*n):
        if comp[x]>=0: continue
        comp[x]=count; stack=[x]
        while stack:
            v=stack.pop()
            for w in graph[v]:
                if comp[w]<0: comp[w]=count;stack.append(w)
        count+=1
    del graph
    cnf=PackedClauses(); top=k*count
    def new(q):
        nonlocal top
        out=list(range(top+1,top+q+1));top+=q;return out
    def exactly(xs):
        cnf.append(xs)
        for a,b in combinations(xs,2):cnf.append([-a,-b])
    def perm(q):
        p=[new(q) for _ in range(q)]
        for row in p+list(map(list,zip(*p))):exactly(row)
        return p
    def color(s,v,c):return comp[s*n+v]*k+c+1
    for v in range(count):exactly(list(range(k*v+1,k*(v+1)+1)))
    ed=sorted({tuple(sorted((comp[s*n+a],comp[s*n+b])))
               for s in range(m) for a,b in data['edges']})
    for a,b in ed:
        for c in range(k):cnf.append(sorted({-a*k-c-1,-b*k-c-1}))
    sections=[('proper',0,len(cnf))];matches=[]
    for j,mm in enumerate(data['mappings']):
        if j==eta:matches.append(None);continue
        section_start=len(cnf)
        if kind=='uniform':
            support=perm(m); palette=[perm(k) for _ in range(m)]
            matches.append(dict(support=support,palette=palette))
            for s in range(m):
                seen=set()
                for a,b in mm:
                    key=(comp[s*n+a],tuple(comp[t*n+b] for t in range(m)))
                    if key in seen:continue
                    seen.add(key);target=new(k)
                    for t in range(m):
                        for c in range(k):
                            old=color(t,b,c);sel=support[s][t];v=target[c]
                            cnf.append([-sel,-old,v]);cnf.append([-sel,old,-v])
                    for c in range(k):
                        for d in range(k):cnf.append([-color(s,a,c),-palette[s][c][d],target[d]])
        else:
            choice=new(3);exactly(choice);palettes=[]
            for mode,arcs in enumerate(SPLIT_TYPES):
                ps=[]
                for s,t in arcs:
                    pi=perm(k);ps.append(pi)
                    for a,b in sorted({(comp[s*n+a],comp[t*n+b]) for a,b in mm}):
                        for c in range(k):
                            for d in range(k):
                                cnf.append([-choice[mode],-a*k-c-1,-pi[c][d],b*k+d+1])
                palettes.append(ps)
            matches.append(dict(choice=choice,palette=palettes))
        sections.append(('motion:'+str(j),section_start,len(cnf)))
    section_start=len(cnf)
    if symmetry:
        origin=4641; require(n>origin,'Y-specific symmetry')
        neighbors=[set() for _ in range(n)]
        for a,b in data['edges']:neighbors[a].add(b);neighbors[b].add(a)
        tri=next((origin,b,c) for b in sorted(neighbors[origin])
                 for c in sorted(neighbors[origin]&neighbors[b]) if b<c)
        sg=[set() for _ in range(m)]
        for a,b in eta_edges:sg[a].add(b);sg[b].add(a)
        seen=set()
        for s in range(m):
            if s in seen:continue
            todo=[s];seen.add(s)
            while todo:
                a=todo.pop()
                for b in sg[a]:
                    if b not in seen:seen.add(b);todo.append(b)
            for c,v in enumerate(tri):cnf.append([color(s,v,c)])
    sections.append(('symmetry',section_start,len(cnf)))
    return dict(clauses=cnf,nv=top,components=comp,count=count,m=m,kind=kind,matches=matches,sections=sections)


def decode_words(built,model,n,k=5):
    positive={x for x in model if x>0}
    return [''.join(str(next(c for c in range(k)
                            if built['components'][s*n+v]*k+c+1 in positive))
                    for v in range(n)) for s in range(built['m'])]
