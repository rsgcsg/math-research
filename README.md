# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**本项目尚未改变 `5≤χ(R²)≤7`。**
[当前状态与突破入口](docs/CURRENT.md) · [结果账本](docs/RESULTS.md) · [路线](docs/ROUTES.md) ·
[统一框架](docs/proofs/hn_unified_framework.md) · [文献地图](references/LITERATURE_MAP.md) ·
[分支与恢复](docs/BRANCHES.md)。

## 2026-09-28：两词修复、三原子极点与真实旋转闭环

新增T140–T142/E113/C025：Y上六个完整运动的最小五色划分支持恰2，删任一运动即可单词满足。
更小的29点实际核心普通χ3，单一不变划分却恰需6色；两份五色划分的均匀混合满足其全部15个局部域。
该核心在六运动单词要求下删任一顶点均可修复，且给Y共同律一个无固定支持的29点柱事件质量≤1/2约束。
**局部15域不是10077点Y的15域；没有HN新界。**
同一个29点系统还存在三原子极点，不能由两词共同律混合得到；这份局部全15域正律却不能延拓至真实五次η轨道。
补齐的86点轨道给三种局部划分总质量的尖锐4/5界，并有达到该界的五色旋转平均。
该轨道有30点不在Y，不宣称已取得原Y15域的新独立分离。
[两词/29点证明](docs/proofs/two_atom_motion_packet.md) · [极点与循环延拓证明](docs/proofs/cyclic_pattern_extension.md) · [当前状态](docs/CURRENT.md)。
`make check-packet`独立重放全Y、29点及86点全部证据；快速小检查为
`python3 -S research/verify_localized_motion_packet.py`。
本轮新提交仍为本地保存，连接未提供远端写入能力；不会把本地提交冒称已推送。

## 2026-09-27：成果已入主线，分支与文档收尾

PR #5已合并为 `4a11fe3f4a957b166fd8f340d950a2a9563a5cec`。
原本地提交 `d5ef85a…`、`875c4f8…` 均保留为真实祖先；无需再次导入旧补丁。
两条旋转研究分支已由运行36304515525按精确SHA归档并删除；本次回读仅有main。
归档标签保留全部历史，旧2026-09-22归档不改动。状态见[本次清单](docs/branch_archive_20260927.json)。
账本至 **T139 / E111 / C024 / Q011**，本次整理不增加数学编号、不改写UNKNOWN。

## 最新成果的准确意义

- **T138/E110：** 整个双自由旋转宿主 `H′Y` 恰五色；Q011已解决，连通性证据已补齐。
- **T139：** 非零平移的单位接触除三类明确无限族外只有有限例外；不是有效指数界，也不是五色延拓。
- **E111：** 一份完整合法Y词使u全部域事件和12个指定二点事件差同时为零，排除这一明确势族的严格分离。
- **认证工具：** 精确二进制整数定价与独立hinted-RUP子集已可运行；不支持任意RAT，也没有15域全词反证。

[平移接触证明](docs/proofs/translated_rotation_contacts.md) ·
[事件反例与认证](docs/proofs/shared_event_pricing.md) ·
[下一构造入口及小例自检](docs/proofs/next_attack_gate.md)。

当前主攻仍是全15域共同律或全词严格分离；几何备线改为可立即验证的有限异中心构造。
**有限下界只需认证所列单位边，不必先穷尽无限宿主的所有例外；正染色结论则须覆盖其声称对象的全部边。**
纯同中心加层、调已被E111排除事件族的权重不再作为独立主攻。

## 重放与范围

```sh
make check        # 全部独立检查入口；不执行新的昂贵搜索
make check-next   # 最新证据、完整几何重建、编码与篡改检查；python3 -S
```

本次新运行通过的是check-next，并确认254份研究源码及继承证书与原检查点逐字节一致；
不是又一次完整make check。历史完整基线及分阶段验证见[原收据](certificates/baseline_next_validation.json)，
本次实际运行见[新收据](certificates/publication_cleanup_20260927.json)。一般定理仍依赖书面证明。
最后移除已完成的一次性传输/归档工作流，仅保留常规只读verify.yml。
搜索与独立认证分离；先阅读[AGENTS.md](AGENTS.md)。
