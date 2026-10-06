"""Exact integration bookkeeping, not a mathematical proof or a search.

Checks the canonical ledger, JSON syntax, Python syntax and local file targets.
Historical raw material under references/unverified is retained, not promoted.
"""
import ast
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result

def audit():
    if not __debug__:
        raise RuntimeError('Verification requires assertions enabled')
    syntax = 0
    for p in sorted((ROOT / 'research').rglob('*.py')):
        ast.parse(p.read_text(), filename=str(p.relative_to(ROOT)))
        syntax += 1
    documents = [ROOT/'README.md', ROOT/'AGENTS.md', *sorted((ROOT/'docs').rglob('*.md')),
                 ROOT/'references/SOURCES.md', ROOT/'references/LITERATURE_MAP.md']
    links = 0
    broken = []
    for p in documents:
        text = p.read_text()
        for target in re.findall(r'\]\(([^\s)]+)\)', text):
            if target.startswith('#') or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            target = unquote(target.split('#', 1)[0].split('?', 1)[0])
            links += 1
            if target and not (p.parent / target).exists():
                broken.append([str(p.relative_to(ROOT)), target])
    if broken:
        raise ValueError('broken local file targets: ' + json.dumps(broken, ensure_ascii=False))
    json_count = 0
    for p in sorted((ROOT/'certificates').iterdir()):
        if p.name.endswith(('.json', '.json.gz')):
            raw = p.read_bytes()
            if p.name.endswith('.gz'):
                raw = gzip.decompress(raw)
            json.loads(raw, object_pairs_hook=unique_keys)
            json_count += 1
    ledger = (ROOT/'docs/RESULTS.md').read_text()
    counts = {}
    for kind, last in [('T',169), ('E',124), ('C',32), ('Q',11)]:
        ids = [int(x) for x in re.findall(r'^\|\s*'+kind+r'(\d{3})\s*\|',ledger,re.M)]
        if len(ids) != last or set(ids) != set(range(1,last+1)):
            raise ValueError('missing/duplicate canonical IDs: ' + kind)
        counts[kind] = last
    manifest_paths = ['Makefile'] + [str(p.relative_to(ROOT)) for p in sorted((ROOT/'research').glob('*')) if p.is_file()] + [str(p.relative_to(ROOT)) for p in sorted(ROOT.glob('requirements*.txt'))]
    manifest = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in manifest_paths}
    return dict(status='PASS', python_syntax_files=syntax, json_certificate_files=json_count,
                local_file_targets=links, ledger_ids=counts, source_files=len(manifest),
                source_manifest_sha256=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                scope='Integration syntax, parseability, exact ID coverage and local file targets only. '
                      'Not exhaustive anchor checking, new theorem validation, or remote publication.')

if __name__ == '__main__':
    print(json.dumps(audit(),ensure_ascii=False,indent=2))
