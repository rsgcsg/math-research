# Hadwiger–Nelson research

目标：解决原始 Hadwiger–Nelson，或证明足以决定它的结构定理。
**原始问题未解决；本轮没有普通平面色数新界。**

[当前研究状态](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[路线与淘汰理由](docs/ROUTES.md) · [结果账本](docs/RESULTS.md) ·
[文献地图](references/LITERATURE_MAP.md)

## 2026-09-21：完整无限旋转轨道恰五色

[T129–130 / E100：完整证明](docs/proofs/dyadic_cyclic_orbit.md)。
对既有10077点Y，实际无限点集 `O=∪_(n∈Z)uⁿY` 的全部单位距离图恰五色。
三个完整词给出最小标号周期3；一条可手算的实际单位边排除周期1和2。
所有高次返回、所有跨层边和原点的无限星均已覆盖，不是抽象一步条带。

一般的两候选赋值判据把无限指数核验压成有限运算；结合一维有限状态，
得到给定代数单旋转实际轨道的可计算染色判定。新证书由不同数域算术独立重放，
190467项边颜色义务、14种篡改拒绝和原有14域完整审计均已执行。
**新三相律的旧14域全部失配；旧14+u仍未知，不是HN新界。**

## 继承的近期结果，不重复记作本轮成果

[T127–128 / E098](docs/proofs/five_word_quartet_completeness.md)：
同m≤5等权五色划分的完整律由四点信息决定；任意权、每份≤5支持时五点恰好足够。
E097/E099两个新编码仍未决定旧14+u，固定支持失败也不是全部proper空间的负证据。

[T125–126 / E095–096](docs/proofs/salem_sextic_four_coloring.md)：
六次Salem整个数域恰四色，114点267边的无三角形顶点临界见证；
一般阿贝尔Cayley三色高度判据及连续幂方向的2/3/4色完整阈值。

此前的E083已给Y上五词共同满足旧14完整域；T116–118给R₂整环四色、
真实最小分母层与有限精度天花板；T122–124给共尾量词、非CM几何与低色宿主筛选。
详细证明、历史UNKNOWN与退出条件保持在上述canonical入口。

```text
references/      原始来源、文献地图、未经重放的历史输入
docs/            canonical 状态、依赖、结果账本、完整证明
research/        精确数学程序；搜索与独立检查分离
certificates/    可独立重放见证和来源绑定
```

标准库独立验证：`make check`。只重放本次入口：`make check-orbit`。
其他近期入口：`make check-salem`、`make check-quartet`。
SAT／NumPy仅用于搜索生产器，不属于本次独立检查器的依赖。
证据规则见 [AGENTS.md](AGENTS.md)。GitHub研究分支发布不等于自动合并main。
