# 分支、成果与恢复

## 当前审计：2026-09-29

起点`research/rotation-rank2-20260926`的482b530已是远端main祖先，
本地main先快进到`a885b67c172726e14884cb43cd37b965dbb32575`。
本轮在`research/consolidation-20260929`吸收4c3e231并开展新工作，不覆盖独有历史。

| 远端分支 | 本轮回读的精确头 | 处理与数学状态 |
|---|---|---|
| main | a885b67c172726e14884cb43cd37b965dbb32575 | 本轮起点，不代表后续发布头 |
| research/full15-coupling-20260928 | 4c3e2313902b40bbfbf63cbc673a45e2951f991f | 加权正规形并入本轮，证明编为T144；旧一次性工作流不是新反证 |
| research/intrinsic-eta-cycle-20260928 | 09926d59b176c1f649aa30f7ec397fb8fa9ef9fa | 已是main祖先，未重造结果 |
| research/joint-continuation-20260928 | b1e4aa8f307010fb7e5322a6cec6403665e32d0e | 已是main祖先，未重造结果 |
| research/triangular-lattice-20260928 | 578bd83c3a47d9a2b9eeed6dc6cbd2651c0f1793 | 独有三角格文稿保留，尚缺下列证据 |
| research/mixed-motion-20260929 | 384275f1c655794b8efccfd75dfd31a8bc2d03d2 | 在三角格文稿上增加工作流，没有新的数学证据 |

三角格文稿声称9624代表、79007接触及Y+Λ恰五色，但这两个分支均不存在文中引用的
`certificates/triangular_lattice_five_coloring.json`、`research/verify_triangular_lattice.py`、
`research/search_triangular_lattice.py`。登记为未独立重放的历史主张，不作为本轮定理或退休平移路线的依据。
未合并该主张进主结果，也未删除远端分支。历史未发布f986eb0a对象不在本地，T141–T143仅留占位。

本轮移除已被标准Makefile替代的`full15-coupling.yml`一次性工作流；原内容可从4c3e231恢复。
常规verify.yml保留；本地验证与远端CI状态分别记录。最终发布以Git头与验证收据为准。
[本轮本地验证收据](../certificates/consolidation_20260929_verification.json)保留完整及补充运行的准确范围。

## 2026-09-27历史快照：当时收尾完成

两条旋转研究分支的全部提交均已进入main，包括原本地d5ef85a…与875c4f8…的完整Git对象历史。
PR #5的合并提交为4a11fe3f4a957b166fd8f340d950a2a9563a5cec。
本次运行36304515525验证后按精确头SHA归档并删除两条分支，回读只保留main、无待合并PR。

| 原分支 | 精确归档头 | 标签 |
|---|---|---|
| research/rotation-integration-20260926 | 3af5a63622185c1393f8e30efda41609ea223230 | archive/2026-09-27/research/rotation-integration-20260926 |
| research/rotation-rank2-20260926 | 482b53020f36900ab2fcceff801ee2eb84893d94 | archive/2026-09-27/research/rotation-rank2-20260926 |

[实际清单](branch_archive_20260927.json)记录的是归档操作时的main快照；后续文档提交会推进main，
但不改变归档标签。先查精确头、祖先、打开PR及运行任务，再原子建标签/删分支并回读；
旧2026-09-22标签与清单不覆盖，未触碰任何未知并行分支。
本次已移除consolidate-checkpoint与archive-rotation-checkpoints一次性流程，常规verify.yml保留。
历史工作流失败保留在GitHub运行历史，不通过删除日志制造全绿记录。

## 维护约定

main保留已验收代码、证据及真实状态；只为正在执行的代码改动建立短期分支，开放数学问题记录在CURRENT。
已合并分支可归档/删除；独有未合并工作不能静默丢弃。未来新研究仍可正常开分支，
“当前只有main”是时间快照，不是禁止新分支。T/E编号、UNKNOWN和历史收据不因归档改写。

## 恢复一个归档

```sh
git fetch origin 'refs/tags/archive/2026-09-27/research/rotation-integration-20260926:refs/tags/archive/2026-09-27/research/rotation-integration-20260926'
git switch -c research/revisit-rotation archive/2026-09-27/research/rotation-integration-20260926
```

这会恢复当时的整个提交，而非保证其一次性工作流还适用。
最新研究从当前main开始，不需重新应用旧补丁。数学状态只见[CURRENT](CURRENT.md)。

## 2026-09-22历史清理

当时的9条研究分支及1条维护分支均保存在archive/2026-09-22下；
[原清单](branch_archive.json)原样保留。旧准备分支只有输入导出工作流，其唯一内容仍由标签保留。
9月26日重新建立的旋转分支与当时无增量的birank-rotation分支不是同一新增工作，不能混写成果。
