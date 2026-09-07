"""Fetch only the pinned original sources explicitly listed in the manifest."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'references/cache_manifest.json').read_text())
target = root / 'references/cache'
target.mkdir(parents=True, exist_ok=True)
for name, url in manifest['papers'].items():
    assert Path(name).name == name and url.startswith('https://arxiv.org/html/')
    path = target / name
    if not path.exists():
        request = Request(url, headers={'User-Agent': 'math-research-source-cache/1.0'})
        with urlopen(request, timeout=20) as response:
            data = response.read()
        path.write_bytes(data)
    data = path.read_bytes()
    print(name, len(data), hashlib.sha256(data).hexdigest())
