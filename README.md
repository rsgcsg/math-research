# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**目前仍为5≤χ(R²)≤7，本项目没有新普通界。**

[当前进度与真实瓶颈](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[路线与淘汰依据](docs/ROUTES.md) · [结果账本](docs/RESULTS.md) ·
[文献地图](references/LITERATURE_MAP.md) · [分支归档与恢复](docs/BRANCHES.md)

## 2026-09-22：合并E105/C024并清理历史分支

账本至T134/E105/C24/Q10。E105已经运行三种全15域定价策略，新增30个合法词；
三个有限池最终仍为ROUND_LIMIT_UNKNOWN。不是只有输入准备，也不是已得到全词反证。
C024用最小四点实际二色例子证明单运动分别可行不推出共同可行。
[完整证明与实验](docs/proofs/full_law_pricing.md)。

本次将未合并成果归入main，完整验收后归档旧分支；精确SHA与恢复标签见
[归档清单](docs/branch_archive.json)。历史研究代码、证书和UNKNOWN不因清理删除或改写。
目前主攻是完整自由五色关系中的配套模式闭合或共享事件严格分离；
几何备线与全配置上界备线的准确验收标准在CURRENT。

## 已有资产

指定宿主R₂恰四色、R₅恰五色、六次Salem宿主恰四色、实际单u轨道恰五色；
旧14域已有共同正律。全词分离编译、有限支持和小支持辨识、覆盖与等式分离提供工具和边界，
不代替原始HN终局证据。答案5需全局≤5；6需NON5和全局≤6；7需NON6。

## 重放

```sh
make check                 # 所有标准库独立检查，不执行昂贵的新SAT搜索
make check-pricing         # E105有限证据与C024校准
make check-preparation     # 输入验收与重建
```

`check-salem`、`check-quartet`、`check-orbit`、`check-covers`、`check-frames`保留。
Python 3.13.5用于本次完整重放；一般Python 3.10+支持声明不等于逐版本回归。
GitHub Actions的 `Independent research verification` 可手动触发，权限只读，不自动改写仓库。

搜索是另一个过程，需额外依赖；E105实际版本及命令见其证明第7节，旧requirements历史不被静默改写。
`references/`保存来源，`docs/`保存状态与证明，`research/`保存程序，`certificates/`保存证据。
请先读 [AGENTS.md](AGENTS.md)，不把搜索器当成它自己的独立检查器。
