# E105保存词池的支持闭合审计

2026-09-22；来源为[原E105证书与实验](full_law_pricing.md)。

本节重放同一份E105数据，既不新增E/T编号，也不升级为全词结论。
若某一完整模式行在当前剩余列中的非零系数全为正（或全为负），
`Dλ=0, λ≥0`迫使这些列的权重全部为0。删去它们再重复，所得每一步都是必要条件。
全部列被删空时，与`Σλ=1`矛盾；若有列幸存，反过来不保证可行。

对保存的三个最终池独立重算全部15域的矩阵，稠密11词一轮删空；
稀疏21词先删17词、再删4词；复用13词一轮删空。
因此，这些有限池的不可行甚至不需要调用LP就能诊断。它们没有形成最基本的非零支持闭合，
并非已经把全合法空间逼到了只差数值精度的临界面。这个解释仍只覆盖保存池；
未保存的新词可以给这些单向行补入反向系数，故绝不能据此声称全词不可行。
消元仅作当前池诊断，不能把这些词永久排除在未来扩池之外。

以下标准库片段从既有独立检查器重建几何/最大域，并直接从原证书重算消元，
不读LP输出的分离式。本次已原样执行；无需依赖原始搜索环境。
从仓库根目录运行：

```python
from pathlib import Path
from collections import defaultdict
import gzip, json, sys
sys.path.insert(0, 'research')
from audit_full_law_preparation import reconstruct
from verify_full_law_pricing import blocks, check_data
root = Path.cwd()
data, summary = reconstruct(root)
cert = json.loads(gzip.decompress((root/'certificates/full_law_pricing.json.gz').read_bytes()))
assert cert['input_semantic_sha256'] == summary['semantic_sha256']
check_data(cert, data, summary)
expected = {'dense': [11], 'sparse': [17, 4], 'reuse8': [13]}
reports = []
for run in cert['runs']:
    rows = defaultdict(dict)
    for i, word in enumerate(run['words']):
        assert all(word[x] != word[y] for x, y in data['edges'])
        for j, mapping in enumerate(data['mappings']):
            a = blocks(word, [x for x, y in mapping])
            b = blocks(word, [y for x, y in mapping])
            if a != b:
                rows[j, a][i] = 1
                rows[j, b][i] = -1
    active = set(range(len(run['words'])))
    layers = []
    while active:
        removed = set()
        for row in rows.values():
            surviving = {i: v for i, v in row.items() if i in active}
            if surviving and len(set(surviving.values())) == 1:
                removed.update(surviving)
        if not removed:
            break
        layers.append(len(removed))
        active -= removed
    assert layers == expected[run['strategy']] and not active
    reports.append(dict(strategy=run['strategy'],eliminated_per_round=layers,survivors=0))
print(json.dumps(dict(status='PASS',pools=reports,
    scope='Three stored finite pools only; not an all-word obstruction.'), indent=2))
```
