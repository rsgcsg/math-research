"""Restore source-reviewed Git objects losslessly; never trust generated hashes."""
import base64,gzip,hashlib,json,lzma,os,re,subprocess,sys
from pathlib import Path
BASE='82a39606d926cc204a084761755db10a56c8dccc'
TIP='875c4f802125f804039ae43586d3c2a8caa19b3d'
PAYLOAD='093e91294bf5551f3e8c7ba66e96098ab4fb7d0f088a1c54bcd81967958fb21d'
ROOT=Path.cwd()
def git(*args,input=None):return subprocess.check_output(['git',*args],input=input)
def h(b):return hashlib.sha256(b).hexdigest()
def get(s,ty=None):
 if ty is None:ty=git('cat-file','-t',s).decode().strip()
 return git('cat-file',ty,s)
def tree_parts(raw):
 parts=[];i=0
 while i<len(raw):j=raw.index(b'\0',i)+21;parts.append(raw[i:j]);i=j
 return parts
def put(raw,ty,expected):
 got=git('hash-object','-w','-t',ty,'--stdin',input=raw).decode().strip()
 if got!=expected:raise ValueError('object reconstruction mismatch '+expected+' != '+got)
def main():
 if len(sys.argv)!=2:raise SystemExit('path to .xz payload required')
 packed=Path(sys.argv[1]).read_bytes()
 if h(packed)!=PAYLOAD:raise ValueError('transport SHA256')
 data=json.loads(lzma.decompress(packed))
 if (data['schema'],data['base'],data['tip'])!=('hn-exact-git-transfer-v1',BASE,TIP):raise ValueError('identity')
 base_blobs=[r.split(b'\t')[0].split()[2].decode() for r in git('ls-tree','-r','-z',BASE).split(b'\0') if r]
 dictionary=sorted({h(get(s,'blob')) for s in base_blobs})
 if len(dictionary)!=data['hash_dictionary_size']:raise ValueError('base dictionary')
 def literal(entry):
  if set(entry)=={'text'}:return re.sub(r'@@H(\d+)@@',lambda m:dictionary[int(m[1])],entry['text']).encode()
  if set(entry)=={'base64'}:return base64.b64decode(entry['base64'],validate=True)
  raise ValueError('literal')
 pending=[]
 for e in data['objects']:
  if e['encoding']=='shared-rup-seed':pending.append(e);continue
  if e['encoding']=='literal':raw=literal(e['literal'])
  elif e['encoding']=='line-delta':
   old=get(e['base'],e['type']);parts=tree_parts(old) if e['parts']=='tree' else old.splitlines(keepends=True)
   raw=b''.join(b''.join(parts[z['copy'][0]:z['copy'][1]]) if 'copy' in z else literal(z) for z in e['delta'])
  else:raise ValueError('encoding')
  put(raw,e['type'],e['sha'])
 # Only reviewed Python source at the pinned target is materialized before the derived evidence.
 for line in git('ls-tree','-r','-z',TIP,'research').split(b'\0'):
  if not line:continue
  meta,path=line.split(b'\t');mode,ty,s=meta.decode().split();p=Path(path.decode())
  if ty!='blob' or mode!='100644' or p.parent!=Path('research') or p.suffix!='.py':continue
  p.write_bytes(get(s,'blob'))
 sys.path.insert(0,str(ROOT/'research'))
 from audit_full_law_preparation import reconstruct
 from verify_event_pricing import rebuild,bind_events
 from rup_hint_export import export
 context,_=reconstruct(ROOT)
 for e in pending:
  c=e['seed'];tiny=dict(n=4,k=2,edges=[[0,1],[1,2]],events=[dict(source=[0,2],target=[0,3],pattern=[0,0]),dict(source=[0,2],target=[1,3],pattern=[0,0])])
  real=dict(n=len(context['points']),k=5,edges=context['edges'],events=bind_events([c['zero_gap_record']],context['mappings']))
  for key,inst in [('tiny_query',tiny),('zero_gap_query',real)]:
   q=c[key];built=rebuild(**inst,coeff=q['coefficients'],target=q['target'])
   if built['cnf_sha256']!=q['cnf_sha256']:raise ValueError('CNF binding')
   trace=q.pop('drup');q['proof']=export(built['clauses'],trace)
  raw=bytearray(gzip.compress((json.dumps(c,separators=(',',':'))+'\n').encode(),mtime=0));raw[9]=255
  put(bytes(raw),'blob',e['sha'])
 git('read-tree','--reset','-u',TIP)
 # Original author/committer metadata and both original commit IDs were restored too.
 for ref in [BASE,TIP,'d5ef85a26138942ba3ae08a93e31e846133160cb']:
  git('cat-file','-e',ref+'^{commit}')
 subprocess.run(['git','fsck','--full','--no-dangling'],check=True)
 print(json.dumps(dict(status='EXACT_OBJECTS_RESTORED',tip=TIP,tree=git('rev-parse',TIP+'^{tree}').decode().strip(),objects=len(data['objects']))),flush=True)
if __name__=='__main__':main()
