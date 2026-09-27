# 分支、成果与恢复

## 当前：2026-09-27收尾完成

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
