# Hadwiger–Nelson research

目标：突破原始 Hadwiger–Nelson，或证明足以决定它的结构定理。
当前普通平面单位距离色数仍为 **5 到 7**；本项目没有新平面上下界。

从这里开始：[当前工作](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[路线与淘汰理由](docs/ROUTES.md) · [T/C/E/Q账本](docs/RESULTS.md) ·
[经典及最新文献地图](references/LITERATURE_MAP.md)。

最新接续：[τ局部化与完整联合](docs/proofs/tau_localization_joint.md)。
旧双层字符边际被8条跨边排除，放开字符后八个完整运动域已有
共同正修复；下一是加入平移1+η后的自由多词联合。另证分母层的
不变律支持下界5ⁿ⁺¹，但该增长连二色图也出现，非六色证据。

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

此前：[换根、移动枢轴与完整F接口](docs/proofs/quintic_moved_pivot_ceiling.md)。
η(z−P)虽有非F平移量，仍是共同原点换根；四角共同加入的5305点图
可延伸到整个F。继而真正移到1+η(z−P)，新增7条跨其他旋转块的
接触，但4577点全图及95点／338接触接口仍可五色修复。T093证明
两种明确扩大的无限宿主分别χ5，不证明它们联合χ5。停止盲扫中心，
随后执行E060配置的混合部分全等与全色词关系检验。

最新：[完整划分修复与确定性色框天花板](docs/proofs/joint_word_closure_and_frontier.md)。
E061的5084点、24844条实际边上，三个跨副本最大部分全等（域大小
2690/1895/513）有同一完整五色正词；S₅平均修复其全部划分事件及
留在X内的共同运动词。T094同时证明确定性色框不是完整joint的完备
替代：可三染的正素数边形加圆心可要求任意多等变颜色，甚至全平面
任何有限染色都不能对所有平移只差颜色置换。下一优先是未被上述
机制覆盖的事件与**所有proper词的凸分离**。随后E062已经加入原律
无法吸收的平移1、z；五份运动仍被新词共同修复。T094还排除固定
划分原子数的通用完备性；普通HN两端仍均未突破。

继续推进：[全词定价与155词库反例](docs/proofs/joint_column_pricing.md)。
E063已在全部proper五色词中执行150次整数定价；18个混合四点映射
严格排除155词库的所有凸混合，却被一个新词修复。这个新词还同时
修复E062五个完整最大域。C019因此不是HN负证据；下一具体入口是
14个尚未被现有样本同色覆盖的非单位点对，必须用完整预染色查询判定。

继续完成：[全部两端口关系饱和](docs/proofs/quintic_pair_completion.md)。
T095/E064补齐14对，认证X上任意合法两点预染色均可延伸；随后14对
同时同色也有完整正词。停止该配置二端口搜索，转向真正联合接口或
出域重入的完整joint；这不是全体四点关系或原始HN的新界。
进一步给出[T096定量编译](docs/proofs/finite_orientation_joint_compiler.md)：
当前有限方向群内，真正全词joint反证能显式生成实际有限NON5图；
现有库内分离不满足输入条件，真正反证仍未找到。

本次接续：[E065十个最大域](docs/proofs/quintic_full_translation_laws.md)
仍被同一完整正词修复，停止该事件族加预算。
[T097–T098](docs/proofs/near_unit_obstruction_compactness.md)证明固定规模
近单位反例可压成真正单位反例，并排除对Parts/Moser等含三角形
种子直接Mycielski升色的整条路线。点数、边数、高度、证明长度与
外部局部一致性结论分开计量；普通HN仍没有新界。
再换到无三角升色候选后，[T099/E066](docs/proofs/mycielski_collision_refutation.md)
用3208节点有理证书排除Grötzsch的所有碰撞分支，继而排除47点
六色Mycielski图的单位同态及任意精度逼近。小型几何反证已实做，
它淘汰候选，不是给原始HN提高下界。
进一步由一个显式五圈推广：任意带边种子的两次及以上Mycielski
迭代都被同一个障碍关闭，不只是47点单例。

最新接续：[T100](docs/proofs/quintic_host_union.md)证明两种完整 F 宿主
的并集仍恰五色，309 条真正新跨边也被联合修复。换线后
[T101–T102](docs/proofs/kneser_zigzag_ceiling.md)用已读 Zig-zag 定理与
投影顺序／菱形中点关系，统一排除所有 topologically 4-chromatic
图的平面单位同态（允许碰撞），包括全部四色以上 Kneser/Schrijver。
这是特定拓扑下界方法的天花板，不是普通色数上界。下一优先转回
真实几何的新完整 joint 义务；原始 HN 仍无新界。

前轮继续：[T103–T104](docs/proofs/module_character_joint_laws.md)不再逐个
试平移：用三词混合修复整个秩八平移模与 60 元方向群在 X 上的
全部最大域，含任意出域重入。群外无限阶旋转 ν 的 271 点最大域已
发现旧混合律缺口，但不是全词矛盾。[T105](docs/proofs/arbitrary_motion_joint_compiler.md)
已把任意有限运动族的真正 joint 反证变成显式有限单位图构造，
不再要求方向群有限。原始 HN 的五色反证及六色全局上界仍未获得。

最新：[T106–T109](docs/proofs/quintic_residue5_ring.md)进一步找到无限环
R=Z_(5)[η,z,ν] 的显式五染公式；模 5 的目标就是 625 点 HG(F₂₅)。
12 字符平均关闭 R 内全部运动及所有 ν 幂的 full joint，故 ν 路线
不再扩搜。已换到真正环外 τ=(−1+3i√11)/10：10077 点的 X∪τX、
49858 条实际边（含170条新跨边）仍五染，独立核验通过。
下一优先为跨 τ 层的完整联合关系；这是结构性正关闭，不是 HN 新界。

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
