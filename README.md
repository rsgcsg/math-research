# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数，或证明足以决定它的结构定理。
**普通界仍为5≤χ(R²)≤7；本项目尚未改变这两个界。**

[当前进度与真实瓶颈](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[路线与淘汰理由](docs/ROUTES.md) · [结果账本](docs/RESULTS.md) ·
[文献地图](references/LITERATURE_MAP.md) · [证据规则](AGENTS.md)

## 2026-09-21：历史收敛与未发布成果整合

归并至T134/E104，不新增定理编号，不把文档、验证或固定模型失败称为HN突破。

- **已决定的宿主与有限关系：** R₂恰4色、R₅恰5色；六次Salem宿主恰4色；
  实际无限单u轨道∪uⁿY恰5色。Y的五词旧14完整域共同律已认证。
- **严格工具：** 全词分离的有限几何编译、有限支持/组合补全等价、小支持四/五点辨识、有限覆盖正规形。
- **方法边界：** 幂零覆盖不能修复指定旧表示；但任意有限部分运动都有等式分离覆盖，
  当前实例有限可解群已足够。等式分离不等于合法染色，更不等于完整共同律。

[最新两轮证明：T131–132](docs/proofs/joint_cover_monodromy.md) · [T133–134](docs/proofs/finite_frame_separation.md)

## 现在到底缺什么

旧14域＋u的**全部合法五色划分上的同一个概率律**仍未知。E084/E097/E099的UNKNOWN保持原样。
不能合并分别成立的子系统正律，不能把固定支持或群类的失败送进全词反证。
主攻是保留所有实际边和完整模式行的全词定价/分离闭环；几何与全局上界各保留一条备线。
精确判据和停止条件见[CURRENT](docs/CURRENT.md)。

原始答案不预定为6：答案5需全局≤5；答案6需有限NON5和全局≤6；答案7需有限NON6。

```text
references/      原始来源、文献地图、未经重放的历史输入
docs/            当前状态、依赖、账本与完整证明
research/        精确数学程序；搜索与独立检查分离
certificates/    可独立重放的见证、来源绑定与验证收据
```

Python 3.10+标准库独立检查：`make check`。
`check-salem`、`check-quartet`、`check-orbit`、`check-covers`、`check-frames`分别重放对应证据。
`make setup`只用于重跑需要额外库的搜索。验证范围与发布状态以CURRENT和本次收据为准。
