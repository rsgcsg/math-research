# 分支、历史归档与恢复

2026-09-22。研究进度只看 [CURRENT](CURRENT.md)，分支不是待办事项清单。
本页记录本次整理规则；最终执行状态、精确SHA与归档标签见 [branch_archive.json](branch_archive.json)。

## 本次处理

开始时有10个分支（main加9个研究分支）。其中7个旧研究分支的提交已进入main；
`full-law-loop-20260922`另有E105/C024实质增量，先验收并合并；
`full-law-pricing-20260921`仅有一次输入导出的工作流，保留原提交归档，不并入失效的恢复流程。
`birank-rotation`与`cyclic-orbit`指向同一旧提交，没有额外双旋转成果。

原研究代码、数学证明和证书不因分支清理而删除。每个拟删除分支先保留
`archive/2026-09-22/<完整原分支名>`标签，SHA必须等于核对的分支头。
归档标签保留完整Git历史，与会到期的Actions artifact不同。
新归并的E105仍是ROUND_LIMIT_UNKNOWN；合并不是宣称15域可行或不可行。

删除只作用于明确白名单内的分支，不触碰main、不遍历删除未知分支：
检查精确头SHA、合并祖先关系（准备分支须核对唯一文件增量）、打开的PR和未完成的工作流；
归档创建与删除使用原子push和逐引用的expected-SHA lease。任一分支被并行更新即停止，
不以强制覆盖继续。执行后再读取远端引用核对。临时维护分支也在合并后按相同规则归档。

## 今后的最小约定

main保存已验收的程序、证据和真实状态；一项正在执行的研究最多开一个短期分支。
没有正在进行的代码改动时，不为开放数学问题预先保留空分支。
已合并分支验收后归档/删除；未完成但有独有工作则保留活动分支，或明确标注后归档，不能静默丢弃。
最多三条活动研究路线是研究上的默认收敛习惯，不是自动删除条件。
历史失败和UNKNOWN继续保存在账本，不因分支删除而重写。

## 恢复旧工作

从清单选一个标签，例如：

```sh
git fetch origin 'refs/tags/archive/2026-09-22/research/full-law-pricing-20260921:refs/tags/archive/2026-09-22/research/full-law-pricing-20260921'
git switch -c research/revisit-pricing archive/2026-09-22/research/full-law-pricing-20260921
```

上述命令恢复当时的整个提交，不表示其一次性工作流现在仍能运行。
新E105搜索使用 `research/build_full_law_pricing.py`；独立证据重放使用 `make check-pricing`。
全仓验收使用 `make check`。保留的 `verify.yml` 是手动触发、只读、无自动提交的验收流程，
不重新执行昂贵SAT搜索，也不把运行成功称作HN新界。
