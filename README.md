# Hadwiger–Nelson research

目标是决定欧氏平面的单位距离色数。当前没有解决原问题；项目中的局部
六染色、条件不可满足和结构类比都不等于新的平面上下界。

开始阅读：[当前工作](docs/CURRENT.md) · [路线与关系图](docs/ROUTES.md) ·
[结果和实验账本](docs/RESULTS.md) · [外部资料](references/SOURCES.md)。

最新整体重审：[接口、上下界与5/6/7](docs/proofs/interface_synthesis_v2.md)；
新结果：[根点支持与真实双gate耦合](docs/proofs/rooted_coupled_gate.md)。
接续：[根接触同步修复与域外校准](docs/proofs/root_contact_repair.md)。
新分类：[七匹配与二接触完整关系](docs/proofs/spindle_joint_support.md)。
几何筛选：[两锚锁域与跨边约束秩](docs/proofs/pose_field_lock.md)。
最新重审：[pair推广与终局优先级](docs/proofs/pair_framework_priority_v4.md)；
新限制：[单模与有限多模首层编码的上限](docs/proofs/residue_method_obstruction.md)。
最新推进：[任意有限精度仍不能绕过谱限制](docs/proofs/higher_residue_precision.md)。
最新几何：[无限三角格中心与双共轭阵列恰五色](docs/proofs/multicenter_arrays.md)。
最新续研：[细分中心的三状态定理与完整接触编译](docs/proofs/refined_center_arrays.md)。
最新收敛：[有限修复反例与全调色板拆分](docs/proofs/background_repair_obstruction.md)。
最新推进：[无锚姿态秩与整个数域的无限平移层](docs/proofs/free_pose_and_field_stacks.md)。
最新收敛：[完整三角格平移层的五染色](docs/proofs/triangular_field_stacks.md)。
几何归约：[二次旋转的虚拟原域枢轴](docs/proofs/quadratic_virtual_pivot.md)。

```text
references/       外部论文索引、原始历史资料
docs/            当前状态、研究路线、结果账本、完整证明
research/        精确检查与有限搜索程序
certificates/    可重放见证、输入和验证摘要
```

基本检查只需要 Python 3 标准库：

```sh
make check
```

需要重新做 SAT 搜索或符号代数时：

```sh
make setup
make explore
```

约定见 [AGENTS.md](AGENTS.md)。研究允许发散，但每约三轮实验做一次收敛：
问具体例子是否有更简单的机制、成熟理论是否已覆盖它、哪些分支应该合并。
本仓库不维护额外的任务系统；以上三个研究文档就是小型项目记忆。
