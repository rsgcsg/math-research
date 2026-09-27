# E106：真实η/u交换方格；列边查询仍UNKNOWN

> 2026-09-26 主线整合：来源提交 `482b53020f36900ab2fcceff801ee2eb84893d94`。
> 本文编号已按主线消歧；旧 T125 与主线 T129 相同，不重复登记。
> 原 Python/JSON 字节保留，内部旧编号只在该来源提交的命名空间解释；映射见
> [整合来源记录](../../certificates/rotation_integration_provenance.json)。历史运行/审读记录不冒称本轮执行。


2026-09-26。下文保存原几何构造及 UNKNOWN 搜索记录。
随后 [T136/E108](rotation_orbit_five_coloring.md)独立证明包含本点集的
完整无限旋转宿主恰五色，所以本交换方格的完整诱导图也恰五色。
这是新证明，不把旧求解器状态改写为 SAT，也不声称旧生产器枚举了全部点对。

为越过“不相容的算子表示”与“真实几何矛盾”的混淆，本次直接构造

\[
Z=Y\cup\eta Y\cup uY\cup\eta uY,\qquad\eta u=u\eta.
\]

所有重合点按精确32维数域坐标识别，不保留不同路径的虚假副本。
不冻结E083色词、算子、边际或E092身份作用。初始图只取四份Y的全部
实际边的运输像；这些都是真实单位边，但未声称已经是Z的诱导图。

| 项目 | 精确值 |
| --- | ---: |
| 去重顶点 | 29669 |
| 坐标公共分母 | 7680 |
| 运输边出现次数 | 199432 |
| 去重列边 | 149822 |
| Z的潜在无序点对数 | 440109946，**未穷举** |
| 两个η方向的副本交集 | 各5289点 |
| 其余四对副本交集 | 各29点 |

仅执行一次20000冲突预算的自由五染查询，得到UNKNOWN
（求解器记录20002次冲突）。没有找到正词或负证书，故未进入计划的
全实际单位边枚举阶段。预算统计是搜索元数据，不是检查器独立证明。
这不证明图难染、不可五染或任意joint不可行，也不推翻E092子问题。

独立检查器采用逐次施加u、η的构造，交叉核对交换性，并重建全部
物理识别和运输边；它没有导入生产器或SAT。报告明确
`all_actual_pairs_enumerated=false`及`GEOMETRY_ONLY_NO_COLORING_CONCLUSION`。
九种档案篡改均拒绝；另有独立极小阳性与全点对分支自测，避免只测试
UNKNOWN路径。`python -O`拒绝运行。

这次不通过增加同一SAT预算续跑，而转向
[T125完整旋转轨道编译](valued_rotation_orbits.md)：先消去全部远程
返回与单位接触的无限量词，再选择真正有限程模型。E095保留为未知
几何实例，不标为被淘汰或已证不可能的方法。

- [查询档案](../../certificates/dyadic_commuting_patch.json)
- [生产器](../../research/dyadic_commuting_patch.py)
- [独立检查器](../../research/verify_dyadic_commuting_patch.py)

```sh
.venv/bin/python research/verify_dyadic_commuting_patch.py --mutations
```
