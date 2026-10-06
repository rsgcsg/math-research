# 2026-10-06 统一分支与成果来源

本次起点为远端main `3009eda28c26334bc8063913af74031cc7bcd9f4`。
逐引用头SHA、差异分类与最终发布状态见 [integration_sources.json](integration_sources.json)。
主线使用一套CURRENT；开放数学问题不是必须保留一个空分支的理由。

## 处理原则

先保留全部远端头/标签与本地独有Git提交，再统一内容；不丢弃历史，不强推，不按日期盲选文件。
7–10号PR按原提交纳入同一整合历史；共享文档以当前状态为准，完整旧文档可按原SHA恢复。
重复SHA和已被主线完整纳入的代码不复制计算成果。任何并行更新都需重新核对，不删除未知新分支。

本地cycle-descent的T141–143填补原主线空缺。full15-certified中四个同名但独立的模块加legacy_前缀；
只调整其内部模块引用，保存的原色词与负证书不改变。更强主线实现不被旧文件覆盖。
数学结论与范围对应关系见 [ID_ALIASES](ID_ALIASES.md)。

## 可恢复归档

远端引用计划归档为 `archive/2026-10-06/<原分支名>`；本地Git包的头则在同前缀local下按来源命名。
归档目标必须与初读头完全相同。删除旧分支只在整合发布成功、归档回读一致、相关PR已处理且无运行任务时执行。
未执行的归档/删除绝不标为完成，最终实际状态在机器清单中。

```sh
git fetch origin --tags
git switch -c research/revisit archive/2026-10-06/research/q-defect-20261006
```

本地完整历史包也保留所有读取的头；无网恢复不依赖会过期的Actions下载链接。
独有未提交实验保存在references/unverified，进入仓库只代表保全，不代表认证。
