# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**本项目未改变普通5≤χ(R²)≤7界；任意支持full15仍未决。**

[当前成果与真实瓶颈](docs/CURRENT.md) · [结果账本](docs/RESULTS.md) · [编号映射](docs/ID_ALIASES.md) ·
[统一证明框架](docs/proofs/hn_unified_framework.md) · [路线与淘汰理由](docs/ROUTES.md) ·
[分支、来源与恢复](docs/BRANCHES.md) · [文献地图](references/LITERATURE_MAP.md)。

## 统一基线已落地（2026-10-06）

PR #11已把可读取的本地成果和远端研究分支归入main。远端只保留main；
11个研究分支和1个维护分支已按原SHA归档，连同更早归档及4个本地检查点，共保留28个标签。
原提交是真实Git祖先或明确归档，不只复制文件；旧失败与UNKNOWN不因整合改写。

统一账本为T001–T169、E001–E124、C001–C032、Q001–Q011。编号是证据索引，不是169次原问题突破。
T141–143已恢复；广义奇轮旧T160现T166，18边模型最优13现T167，完整34边最优12仍T162。
九Q计数包络为T168；独立整数平移证据为T169。完整对应关系见编号映射。

同一冻结源码的70条不同Python检查已在8个隔离工作树全部通过，原始日志永久入库；
这是完整命令覆盖，不是一次串行make check。本次收尾重新验收日志、源指纹、历史和文档，
没有重跑这70条数学检查，也没有改动研究程序或原证书。
[原始完整验收](certificates/unified_integration_validation.json) · [本次收尾复核](certificates/unified_closeout_validation.json)。

```sh
make check                     # 全部已接入的独立检查，不执行新研究搜索
make check-integration         # 编号、JSON、Python语法及本地文件引用
make check-packet check-cycle-descent
make check-q-joint-boundary-gap check-q-boundary-gauge-lift check-two-partition-w22-audit
```

仅保留手动、只读的verify.yml；一次性导入、封存、归档工作流均已移除。
未完成的边界端点实验和已纠正旧稿在references/unverified内单独保存，不冒充有效证书。
请先读[AGENTS.md](AGENTS.md)。搜索器和独立检查器分开；一般证明不因程序PASS就被称为形式化或同行评审完成。
