# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**本项目尚未改变5≤χ(R²)≤7。**
[当前状态](docs/CURRENT.md) · [已有编号账本](docs/RESULTS.md) · [历史路线](docs/ROUTES.md) ·
[统一框架](docs/proofs/hn_unified_framework.md) · [文献地图](references/LITERATURE_MAP.md)。

## 2026-09-28：原15完整域的三支持缺口已认证闭合

任意实权的至多三个完整划分都不能形成原15域共同律；两种权重型、六个η运输情形均有独立RUP反证。
这只证明**若共同律存在则至少四支持**，不是任意支持无解或普通HN新界。
另得任意三个完整划分总质量≤9/10的必要界；一般矩阵常数尖锐，在Y中未证明可达。

[完整六情形证明](docs/proofs/full15_support_exclusion.md) · [质量界与反例](docs/proofs/ternary_concentration.md) ·
[证明流完整性修复](docs/proofs/proof_stream_integrity.md)。
标准库独立重放：`make check-full15-support`。更大支持查询的未认证否定/UNKNOWN与验证范围在CURRENT。

## 实际几何推进：所有整数平移副本一起仍恰五色

不是有限窗口推断：9740个代表、60229条完整接触类型和一份9740字母词，给出整个
`Z_Y=⋃_{n∈Z}(Y+n)` 的公式 `c(q_i+n)=a_i+n mod5`。
[完整证明与边界](docs/proofs/integer_translate_five_coloring.md)。
`make check-translate-kernel`重新计算全部接触并验证公式，`make check-unit-translate`另验两副本证据。
同Y沿1方向继续加整数层的NON5路线因此停止；不是全平面上界或全15域共同律。

## 已有结果：PR #6的共同观察系统被三词精确修复

此前PR #6证明：`S=F∪Γ∪完整η域` 的五色共同律**最小划分支持数恰为3，允许任意实权重**。
三份完整10077点五色词通过149574项实际边检查和34项明确的分布义务；
两种η支持匹配的二词情形由独立RUP反证全部排除。
三词律还是整个S可行多面体的极点。**它只满足原15个完整域中的7个，不是15域正解。**

- [完整定义、正负证明和质量界](docs/proofs/eta_joined_minimum_three.md)
- [固定点有限阶运动的调色板正规形](docs/proofs/anchored_eta_normalization.md)：保留支持数和支持匹配，不偷加σ⁵=id。
- [三原子权重分类](docs/proofs/three_atom_weight_types.md)：无二原子解时，只可能等权或1/2、1/4、1/4。

上述结果直接使用已发布09926d59基线的精确几何，**不依赖尚未全部发布的T141–T143代码**。
本轮采用描述性文件名登记，避免与本地历史检查点的既有T/E编号冲突；没有覆盖旧编号或历史UNKNOWN。

```sh
make check-eta-support    # 标准库：真实几何、三词正例、两种反证和40项拒绝测试
make check                # 包含新增入口；不重新执行搜索
```

本地干净基线和GitHub Actions运行36374324777均完成新增入口，退出0，输出逐字节相同。
[本地收据](certificates/eta_joined_local_validation.json) · [远端收据](certificates/eta_joined_remote_validation.json)。
不冒称本轮在最终树上重新完成单次全仓回归；一般结论仍依赖完整书面证明，不是形式化或同行评审声明。

## 已有资产及其边界

T138的整个双自由旋转宿主H′Y恰五色；T139分类平移接触，但不自动给有效窗口或五色延拓。
T140/E112对具有非零有限赋值的共同单旋转底数完成有效接触枚举与有限核校准；
不是一般双旋转平移算法，也不证明所有这些核都可五染。
E111已经排除指定事件势族的严格分离；本轮S正律进一步关闭S内部的全词负搜索。

主攻必须使用尚未修复的八个原始完整域的联合信息；几何备线寻找真实自由五色关系收缩。
有限下界只需认证所列单位边，不必先穷尽无限宿主；诱导图或无限宿主的正结论才需要相应完整覆盖。
整个平面上界另需全配置论证。研究时先读[AGENTS.md](AGENTS.md)，不要将固定支持失败当成任意支持反证。
