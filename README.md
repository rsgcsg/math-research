# Hadwiger–Nelson research

目标：决定普通欧氏平面单位距离色数。**本项目未改变普通5≤χ(R²)≤7界，任意支持full15仍未决。**

[当前状态与瓶颈](docs/CURRENT.md) · [统一账本](docs/RESULTS.md) · [编号映射](docs/ID_ALIASES.md) ·
[完整证明框架](docs/proofs/hn_unified_framework.md) · [路线与淘汰原因](docs/ROUTES.md) ·
[分支与原始成果恢复](docs/BRANCHES.md) · [文献地图](references/LITERATURE_MAP.md)。

## 2026-10-06：无损统一可见远端和本地成果

恢复本地T141–143、独立full15/整数平移证据及Q失配补充；归入PR7–10和Q投影分支。
原始提交由归档引用保存，编号冲突有明确映射：T160的广义奇轮旧号现为T166；
T162的18边最优13现为T167，完整34边最优12仍为T162。
两者不是矛盾。四段Q下包络为T168，不等于完整P/Q/R共同律。

T165/C030已跨过某个单颜色外放松，但没有排除所有合法五色共同律。
未完成端点实验与历史缺失资料保持未认证；没有把整合、测试或分支清理算新HN突破。

```sh
make check                     # 完整标准库检查
make -j2 check                 # 同一依赖图，两任务并行；需要足够内存
make check-integration         # 编号/格式/来源/文件引用静态审计
make check-packet check-cycle-descent
make check-q-defect-lift check-q-defect-scope-audit
make check-q-joint-boundary-gap check-two-partition-w22-audit
```

Python版本、实际覆盖与运行日志见[验收收据](certificates/unified_integration_validation.json)。
搜索与独立检查分离；新搜索依赖不由make check安装。请先读[AGENTS.md](AGENTS.md)。
