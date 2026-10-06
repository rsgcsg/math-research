# 分支、成果来源与恢复

2026-10-06。**统一归并已完成，远端仅保留main，当前没有打开的PR。**
当前工作区以已发布83c36cd432e41fb2cdc7ed82395902ddedb87fd7为收尾基准；旧版本不是另一个活动主线。
[完整原始引用与处理记录](integration_sources.json) · [编号消歧](ID_ALIASES.md) ·
[当前研究状态](CURRENT.md) · [本次收尾验收](../certificates/unified_closeout_validation.json)。

## 1. 哪些历史已经保留

| 归档组 | 标签数 | 内容 |
|---|---:|---|
| archive/2026-09-22 | 10 | 早期研究与当时维护分支；含未并入主线的一次性输入准备流程 |
| archive/2026-09-27 | 2 | 双自由旋转及其归并分支 |
| archive/2026-10-06/local | 4 | cycle-descent、motion-packet、full15-certified、q-defect-capacity的原本地提交 |
| archive/2026-10-06/research | 11 | 全15域、混合运动、三角格、P/Q/R投影和划分不等式等研究头 |
| archive/2026-10-06/maintenance | 1 | 本次统一归并分支 |

合计28个标签。12个本次清理目标在运行37437922972中，经明确白名单、合并祖先、原SHA、
打开PR和活动任务检查后，原子建立标签并删除分支；原有标签未改动。
本轮只复核这项已完成操作，没有再次删除相同分支，也没有新增空研究分支。

PR #11使用合并提交保留历史。#7/#8被GitHub识别为已合并；叠加的#9/#10在确认其提交已进入主线后关闭。
四份原本地提交f986eb0a、b532e714、86a7f6c5、3dc223a7既有独立标签，也都是主线祖先。
这些不是重建成不同SHA的文件拷贝。各分支共享文档的旧版本仍可从其原提交读取。

唯一明确保留而不合并的旧头是5cd52cea：它仅增加一次性输入准备工作流。
它仍由archive/2026-09-22/research/full-law-pricing-20260921保存，没有被当成新数学结果或丢弃。

## 2. 本地与证据的处理

本次36份挂载ZIP包含原31份清单输入和5份后续整合/验收包；23处bundle引用共有42个不同头提交。
全部原清单哈希相同，头提交均为主线祖先或上面的明确归档例外。
恢复的规范Git工作区只保留main和同一批28个标签；原始下载包、补丁和只读散落文件不破坏性删除。
“本地”不包括用户个人电脑尚未上传的仓库。

4个旧full15模块重命名为legacy_，只调整对应调用，让独立证据与主线实现并存。
编号冲突以ID_ALIASES为准，不能凭同名覆盖证书。未完成端点实验与8份历史碎片在
references/unverified单独保存；保全不是认证，旧稿的已知错误不恢复到正式证明。

## 3. 恢复方式

联网恢复一个旧分支：

```sh
git fetch origin --tags
git switch -c research/revisit archive/2026-10-06/research/q-defect-20261006
```

无网恢复本次完整交付：

```sh
git clone -b main /path/math_research_unified_final_20261006.bundle math-research
cd math-research
git remote set-url origin https://github.com/rsgcsg/math-research.git
```

标签和Git历史不会像Actions临时下载地址那样自动过期；本仓库和交付包都保留完整验证日志。
封存收据中的“pending main merge”只记录当时阶段；实际合并/清理状态由integration_sources的
remote_cleanup及当前Git引用给出，不能相互混用。

## 4. 后续约定

main只接纳范围明确、已验收的研究；确有正在修改的源码才开短期分支。
新成果必须区分定理、有限证据、搜索状态和未完成输入，并更新CURRENT、RESULTS和ROUTES。
已有分支归并后再归档/删除，任何并行新增或改动都重新核对；不盲删、不强推、不清除原证据。
常规验证只保留手动只读verify.yml；一次性导入、封存、归档脚本已经移出当前文件树，历史仍可恢复。
