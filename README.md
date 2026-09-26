# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**仍为5≤χ(R²)≤7；本项目尚无新普通界。**
[当前状态](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[结果账本](docs/RESULTS.md) · [路线](docs/ROUTES.md) · [文献](references/LITERATURE_MAP.md) ·
[分支归档](docs/BRANCHES.md)

## 2026-09-26：Q011已解决，完整双自由旋转宿主恰五色

[新T138/E110证明](docs/proofs/rank2_rotation_five_coloring.md)：
整个〈η,u,τ〉Y的2082非零轨道、11261单位接触和30原点邻轨完整重建；
显式η/τ保色、u三周期公式给五染色，继承下界给色数恰5，最小正u标号周期3。
32维生产器和16维独立检查器重算全部几何，不从窗口外推。

新词仅通过τ/η/u三个原运动域，另外12域失配；自由15域共同律仍未决。
同旋转宿主的更多层数不再作为NON5路线。真正瓶颈仍是全自由颜色关系与几何兼容。

同时整合基于旧主线的旋转分支：T135–137/E106–109；与现有T129重复的单旋转定理只保留另证。
[旧编号来源映射](certificates/rotation_integration_provenance.json)防止覆盖main的T125–134/E095–105。
所有旧UNKNOWN与历史证据保持原样；T/E编号不宣称文献优先权。

```sh
make check             # 全部标准库独立检查
make check-rotations   # 导入的旋转证据
make check-rank2       # 新完整双旋转五染和边界
make check-pricing     # E105保存有限池，不是全词负判定
```

搜索与验证分离，范围及运行收据见CURRENT。只读手动GitHub验证入口保留；
新提交的来源和本轮验证以实际收据为准，不借用旧分支过期“本地未发布”描述。
请先读[AGENTS.md](AGENTS.md)。
