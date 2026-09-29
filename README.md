# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**尚未改变5≤χ(R²)≤7。**
[当前状态](docs/CURRENT.md) · [结果账本](docs/RESULTS.md) · [路线](docs/ROUTES.md) ·
[统一框架](docs/proofs/hn_unified_framework.md) · [文献地图](references/LITERATURE_MAP.md)。

## 2026-09-29 第二轮：从七重几何得到无限宿主定理

- **T150：** Haugland的整个84方向加法宿主**恰四色**，原表六种标号均已全局延拓。
  赋值＋CM/Kronecker证明其全部实际单位方向恰是这84个，不是假定没有隐藏跨边。
  下界由21点核的完整三色排除树独立验证。
- 继续扩到`L_m=Σr^j O`，完整方向恰有`42(m+1)`个。第二层的模2商
  **T151严格至少六色**，关闭该商的所有五色公式；这不是实际单位图或平面的六色下界。
- 随后实际检查729点的另一剩余域目标，五/六色查询仍UNKNOWN，没有新全域上界。
  第二层7939点的实际单位图也已独立重建，五色查询UNKNOWN，不构成下界。
  full15任意支持问题仍未决；错误的跨运动同步乘积推论已剔除。

[完整证明与执行结果](docs/proofs/heptagon_cm_module.md) ·
[六份全局公式](certificates/heptagon_table_extensions.json)。
**这是严格的局部研究进展，不是原始HN突破。**

## 2026-09-29：远端归并、完整三原子排除与方法边界

- 原Y的**全部15个完整域不存在至多三原子共同律**，允许任意实权重。
  六种完备情形已有独立重建、RUP反证；不是把求解器UNSAT直接当定理。
- 一般尖锐质量界：无三原子律时，任意三个完整划分至多占9/10。
  另给真实平面构造，说明五色η正规形不能直接推广到六色。
- 继续证明：连通实际χ5单位图仍不能用统一固定阶边际识别任意支持划分律；
  [核心接树的奇偶构造](docs/proofs/connected_partition_marginal_ceiling.md)明确保留其非结论。
- **这些都不是原问题突破。** 任意支持的共同律仍未知；主攻转向跨支持的全词严格势，
  不把m=4、5、6的枚举自动当作下一研究路线。

[完整反证](docs/proofs/full15_three_atom_exclusion.md) · [9/10定理](docs/proofs/three_atom_mass_gap.md) ·
[五/六色正规形区别](docs/proofs/anchored_palette_threshold.md) ·
[本轮结构重审](docs/proofs/research_reassessment_20260929.md)。

已有S子系统仍最少三原子；其正律只通过原15域中的7个。
T138的整个同中心双自由旋转宿主仍恰五色。
远端三角格/混合运动文稿缺失所引用证据，未提升为已验证定理；见[分支审计](docs/BRANCHES.md)。

```sh
source .venv/bin/activate  # make setup可准备环境；全仓检查要求Python≥3.10，CI固定3.13.5
make check-full15-support
make check-eta-support
make check-heptagon-module
make check
```

独立检查仅需Python标准库；搜索另用固定研究依赖。先读[AGENTS.md](AGENTS.md)。
真实有限NON5需要精确单位边与完整不可五染证据；全平面六色上界需要全配置量词。
UNKNOWN、固定词库/周期失败、缺证书的文稿和漂亮新几何都不代替这些义务。
