# T100 / E067：两个完整 F 宿主的并集仍恰五色

2026-09-11。局部研究结果，不改变普通 HN 上下界。

沿用 [T093](quintic_moved_pivot_ceiling.md) 的记号，令
H₀=F∪R∪⋃ⱼTⱼ，H₁=F∪R∪B，j=1,…,4。
此前两宿主分别五色，不曾证明它们的并集五色。

**T100。χ(H₀∪H₁)=5。** 特别地，在这个并集内任意增加 F 中的点、
坐标分母或选取不同有限窗口，都不能得到普通 NON5。

## 完整有限证据与无限延伸

本轮直接生成 S=R∪⋃ⱼTⱼ∪B；没有固定旧宿主的颜色。

| 核验对象 | 精确数量 |
| --- | ---: |
| S 中点 | 5813 |
| 全部无序点对 | 16892578 |
| 实际单位边 | 29740 |
| 不属于任一旧右部内部的新增边 | 309 |
| 完整 F 接口点 | 99 |
| 去重 F–S 接触不等式 | 354 |
| S∩F | {0,1} |

309 的定义是：从 S 的实际单位边中删去所有两端同属
R∪⋃ⱼTⱼ 或同属 R∪B 的边。不是按副本名称粗分所得的跨边数。
每条新增边都参与求解和独立检查。

完整 F 邻点由 T092/T093 的判别式分类给出。检查器重新核验旧宿主
依赖，以及每个换根向量的平方／非平方证据；重新构造全部 354 个接触，
并检查每个接触的单位长度。随后核验一个 S 上的 proper 五色词、
一个 F₁₁² 剩余目标上的 proper 五色词（全部 726 边）、全部接触异色及
0、1 两处重合的颜色一致。它不调用 SAT 或生产器。

所有接口坐标分母与 11 互素。照 T028/T093 的赋值陪集延伸，把剩余
色词扩到整个 F；F 内的所有单位边不跨相应加法陪集。有限词与扩展
在全部接口处相容，故合并为 H₀∪H₁ 的五染色。P⊂F 给出下界五。□

首轮 100000 conflict 预算为 UNKNOWN；后续 1000000 预算找到正词。
本结论只使用可直接检查的正词，不使用搜索时间或 solver 的负标签。
另做过不附加 F 接口的有限自由五染查询，也为 SAT；它被更强的
完整接口正见证涵盖，未另留重复证书。

## 范围与换线

退休 H₀∪H₁ 内的普通 NON5 搜索。不声称任意多枢轴、整个 E、
全平面五／六染，亦不声称该并集的全部部分全等 joint 律相容。
309 条真正新边仍不足以强迫五色矛盾，说明边数增益不能代替完整
颜色关系增益。本轮随后换到 Kneser 候选并得到
[T101–T102](kneser_zigzag_ceiling.md) 的一般性排除，而未继续盲加平移。

## 重放

生产器和检查器是在原 T093 工具上增加严格区分的 schema 2 / union 模式；
原 schema 1 的三例及硬编码范围检查保留。

```sh
.venv/bin/python research/quintic_translated_orbit.py --union --output certificates/quintic_host_union.json
PYTHONPATH=research python3 -c 'from pathlib import Path; from verify_quintic_translated_orbit import verify; r=Path.cwd(); print(verify(r,r/"certificates/quintic_host_union.json",union=True))'
make check
```

[证书](../../certificates/quintic_host_union.json)绑定 Parts/T092 来源 SHA；
点 SHA：`053cb15434b92bffa92bf633674f71f60c98b2a31be91f61883e69ab03fc4a40`；
边 SHA：`d7c3c0d1f1ae61c3ab942525480533e0f4846f1447481fca5dc694b730400fc2`。

## 本轮验证回执

基线 `f3ff45c`，开始时工作区干净；未提交、推送或修改索引。
E067/E068 独立检查均 PASS；两生产器重放与保存证书逐字节一致。
新证书 SHA256：

- E067：`1cba1a7342c176361e880347ac16c539fb36ddf7dfaa0b4b8f4f4d9d5e297e21`
- E068：`5354a52df693b75a2de5420c02dc58cc9080b998d17eed9d012d5d9a14914a57`

六项定向篡改全部拒绝：union schema、实际边数、非法右部色词，
以及 Kneser 集合表、整数权重、前置证书 SHA。两检查入口均拒绝 `-O`。
五个相关 Python 文件 AST、本地文档链接和 `git diff --check` 通过。
新增 E067/E068 入口集成后的完整 `make check` 已退出 0；其后仅补充
文档回执与历史链接。T102 的外部拓扑定理不属于机器回归的证明范围。
