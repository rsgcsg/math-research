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

接续结果：[回缩的全等缺口与剩余平均模型的统一排除](docs/proofs/quintic_congruence_gap.md)。
已找到精确部分全等反例；全部11进剩余平均模型都失败，但新自由色词
仍满足本轮七个联合约束，尚未形成原始HN反证。
随后已实做[跨纤维两锚Parts桥](docs/proofs/quintic_anchor_bridge.md)：2540点
仍五色，五份完整509点副本分布也有正修复；当前瓶颈是接口关系的
真正不相容，而不是事件或副本大小。

此前推进：[六桥与整个共同宿主的五色上限](docs/proofs/quintic_bridge_ceiling.md)。
六桥4125点仍五色；进一步证明旧配置与整个旋转K平面的联合恰五色。
1941个无接触排除和81点有限接口已独立认证，关闭同宿主无限加桥路线。

此前：[方向不变量与径向谱上限](docs/proofs/quintic_direction_and_radial_ceiling.md)。
82个新位置仍只复用两种方向；已构造严格非扭转方向，但有限图仍五色。
进一步认证Parts原点的全部47种平方半径：在当前二次扩域中，任意多
同原点旋转、甚至整个对应47壳宿主都恰五色；这促成了后续换根检验。

此前：[换根、例外接触与全参数五色上限](docs/proofs/quintic_exceptional_contact_ceiling.md)。
根点0、64的整个217壳仍五色；新半径探针只产生恒等边。继而直接
分类777243项全角度接触：仅两个余弦值增添例外跨边，但完整接口
仍可修复，整个指定四副本族恰五色。搜索现以不能被原域专门化、
低色同态或三端口修复吸收的例外接触网络为门槛。

此前：[整个原域加四个例外旋转块仍恰五色](docs/proofs/quintic_fixed_orbit_ceiling.md)。
第五副本候选已执行，两例均未增加真正跨域的接触。进一步穷尽对整个F的
邻点：每种余弦980项无接触、37项有接触；四角联合4069点19560边，
通过74点／296边接口与整个F同时五染。只在F内继续加点的路线已关闭；
完整全等joint仍未决定，普通HN上下界未变。

最新：[换根、移动枢轴与完整F接口](docs/proofs/quintic_moved_pivot_ceiling.md)。
η(z−P)虽有非F平移量，仍是共同原点换根；四角共同加入的5305点图
可延伸到整个F。继而真正移到1+η(z−P)，新增7条跨其他旋转块的
接触，但4577点全图及95点／338接触接口仍可五色修复。T093证明
两种明确扩大的无限宿主分别χ5，不证明它们联合χ5。停止盲扫中心，
下一优先为E060配置的混合部分全等与全色词有效的关系分离。

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
