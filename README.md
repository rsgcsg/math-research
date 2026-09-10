# Hadwiger–Nelson research

目标：突破原始 Hadwiger–Nelson，或证明足以决定它的结构定理。
当前普通平面单位距离色数仍为 **5 到 7**；本项目没有新平面上下界。

从这里开始：[当前工作](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[路线与淘汰理由](docs/ROUTES.md) · [T/C/E/Q账本](docs/RESULTS.md) ·
[经典及最新文献地图](references/LITERATURE_MAP.md)。

统一对象是“具有二维单位实现的整数关系系统，能否满足完整 k 色约束”。
下界需要一个有限真实反证；上界需要覆盖所有有限真实配置。不得以
条件 activation、固定编码失败、投影失败或 SAT UNKNOWN 替代它们。

本轮新证明包括[整数关系格／Gram共尾归约](docs/proofs/hn_relation_lattice.md)、
[安全域完整joint天花板](docs/proofs/invariant_joint_ceiling.md)、
[高密度但整个宿主恰五色的数域塔](docs/proofs/dense_five_color_tower.md)。
新有限检验：[五次旋转三中心](docs/proofs/quintic_core_probe.md)与
[两角度联合](docs/proofs/quintic_mixed_angle_probe.md)均有完整Parts图回缩，
不是六色证据。其他证明从账本定位，不再维护多份“最新路线”。

```text
references/      原始来源、文献地图、未经重放的历史输入
docs/            canonical状态、依赖、结果账本、完整证明
research/        精确数学程序；搜索与独立检查分离
certificates/    可独立重放见证和来源绑定
```

基本检查只需 Python 3 标准库：

```sh
make check
```

重新运行 SAT／符号代数搜索需要本地环境：

```sh
make setup
make explore
```

证据规则见 [AGENTS.md](AGENTS.md)。外部深定理、书面证明、有限认证、
搜索观察、猜想分别记录；本地研究不自动包含GitHub发布。
