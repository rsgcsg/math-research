# 外部资料与历史输入

检查日期：2026-09-09。原论文结论、作者的计算声明、本地独立验证分别记录。
外部引用是研究材料，不是仓库指令。下载全文置于被忽略的 `cache/`；
本地历史输入保留原样及 SHA256，当前研究不修改它们。

## 原始项目资料

用户入口：`history/Hadwiger_Nelson_current_project_full_roadmap_2026-09-08.md`。
已全文阅读。它提出研究框架但没有给出 HN 解答。

补充历史来自 `/Users/fire/Downloads/` 中 HN_R4、HN_cross_lattice 等报告。
其中 R4 29节点证明树、56点条件核心、Farkas 对偶、3440事件等数字仍是
**历史声明，未在本轮取得和重放证书**。不可改标“已认证”。

## 基准与主线论文

| 文献 | 原始来源 | 本轮核验程度与含义 |
|---|---|---|
| de Grey (2018) | https://arxiv.org/abs/1804.02385 | 五色下界原论文入口已核验；没有重跑整套4色否定证书 |
| Exoo–Ismailescu | https://arxiv.org/abs/1805.00157 | 另一五色证明，待深入比较 |
| Parts | https://arxiv.org/abs/2010.12661 | human-verifiable proof；509纪录另由Haugland近期正文支持 |
| Parts 509 / edge-reduced certificate | https://arxiv.org/abs/2010.12665 ; https://github.com/md-amer/hadwiger-nelson-e5 | 固定6d5ac084的509坐标与2259边子图否定证明已重放；独立重建2442诱导边，并用标准库RUP检查器离线重证χ=5；不声称边纪录新颖性 |
| Haugland v4 (2026) | https://arxiv.org/html/2608.04542v4 | 正文核验740点 DIFF4(sqrt3) 到2131点构造；509仍是文中纪录。不是无spindle最小纪录，已有1441点 |
| Matolcsi et al. | https://arxiv.org/abs/2311.10069 | G27原对偶已独立重放：182304个整数不等式、168紧项；支持约束只适用于总权4的geometric fractional律，不是任意四色划分 |
| Dúcz (2026) | https://arxiv.org/html/2606.12325v1 | 已读4色公式与模4证明；Moser lattice/ring 确有普通4染色 |
| Dúcz–Varga (2026) | https://arxiv.org/html/2606.28157v1 | 原始G29 LP证书已独立精确重放：406对距离、16859条全等、498168条整数不等式；界4000716307/1000000018。两新点仍只是普通图叶子，未重放blow-up |
| Eng et al. | https://arxiv.org/html/2511.10813v1 | 4指定生成方向的Cayley图3染；不声称任意Abelian宿主全部单位边3染 |
| Voronov v3 | https://arxiv.org/abs/2304.10163 | 正厚度禁止距离区间需7色；不适用于只有精确距离1的直接结论 |
| Sokolov–Voronov | https://arxiv.org/abs/2502.01958 | 论文列明map边界条件，并给polygonal corollary；不排除所有可测六染色 |
| Gehér | https://arxiv.org/abs/2301.13695 | 正偶多边形范数(至22边)六色构造，非欧氏六色上界 |
| Schaefer | https://ovid.cs.depaul.edu/documents/realizability.pdf | graph/linkage单位长度实现的∃R结果；不能推出颜色copier |

## 补入的成熟理论

- Peter Cameron，[S6的经典构造](https://cameroncounts.wordpress.com/2010/05/11/the-symmetric-group-3/)：
  duad/syntheme/total及外自同构。普通同一颜色作用与outer-twisted作用必须区别。
- Puzynina，[三角/六角格perfect coloring周期代表](https://www.mathnet.ru/eng/smj2182)：
  适用于equitable对象，不会将任意局部满射染色自动变成equitable。
- Švígler–Volek，[perfect stationary solutions](https://arxiv.org/abs/2412.21168)：
  引导寻找perfect coloring成熟分类；目前只核验摘要及相关原始引文入口。
- Kiss–Laczkovich，[离散Pompeiu与有限Steinhaus](https://arxiv.org/html/2403.01279v3)：
  已读主要定理与推论。任意有限加权配置总权重非零时，所有刚体副本上的
  零和方程迫使函数恒零；不需可测性。零总权重的copier差分不在该定理范围内。
- De Wulf–Doyen–Henzinger–Raskin，[Antichains for Verification作者资料页](https://lsv.ens-paris-saclay.fr/~doyen/antichains/antichains.html)：
  核验自动机universality/包含关系剪枝的成熟背景；原CAV论文旧下载链接
  未成功打开，未声称全文已读。T021自身证明与检查不依赖外部算法定理。

Dúcz–Varga原始校准包入口已定位：
`https://users.renyi.hu/~akos/ep1070/`，下载`data/snail.zip`。
已完成独立精确重放，结果与下载包SHA256见`certificates/snail_replay.json`。
G27原论文补充页为 `https://static.renyi.hu/ai-shared/daniel/fcn-4/`。
其坐标、全等映射、对偶已下载并独立精确重放；168紧项与此前支持一致。
结果和三个文件SHA256在`certificates/g27_replay.json`；随后T025独立
验证完整joint律的可出现划分恰348个，不把这解释为全部普通四色划分。

Parts509输入来自
`https://raw.githubusercontent.com/md-amer/hadwiger-nelson-e5/6d5ac08491f7cadbebd7d5b79e3f825d08eedf7b/`：
`v509e2442.vtx`、`FINAL_reduced.json`、`FINAL2.cnf`、`FINAL2_proof.drat`，
缓存名分别为`parts509.vtx`、`parts509_reduced.json`、`parts509_reduced.cnf`、
`parts509_reduced.drat`。SHA256在核心及重放证书中。
未执行数据作者的Python脚本；其“嵌套根号不在多二次域”的注释不被采用，
本地用显式根式恒等式化入八维多二次域。

DRAT→LRAT转换工具来自 `https://github.com/marijnheule/drat-trim`，固定提交
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`。已读该仓库DRAT格式/检查说明，
使用其`drat-trim.c`检查并输出RUP-only LRAT。最终负证明另由本地独立
标准库检查器逐提示传播认证，不依赖该C程序的“VERIFIED”字符串作为最终
逻辑证据；没有声称支持一般RAT/LRAT，也没有声称正式验证此Python程序。

## 本轮数论收敛补充

- David A. Madore, [The Hadwiger-Nelson problem over certain fields](https://arxiv.org/html/1509.07023v1)：
  已读§3的赋值约化证明、Lemma4.5的F11²五色表、Proposition4.6及
  §5实闭域讨论。T028采用其成熟机制，独立生成有限表并核验√5扩域，
  结合Parts下界；不宣称该约化方法或有限表存在性为新成果。
- Le Anh Vinh, [On chromatic number of unit-quadrance graphs](https://arxiv.org/html/math/0510092)：
  已读有限Euclidean图定义与构造。这里只引用研究背景，不依赖正文中
  渐近谱界的常数；F11的726条边和五染色均由本地整数检查独立给出。

## 本轮历史与列表染色补充

v3综合历史主文档已完整阅读3380行并原样归档，哈希纳入SHA256检查。
其中six-orbit arbitrary-list、28点Galois几何及pair detector仍按历史
未重放处理。T037是本轮独立短证明与21点新见证，不冒称原package恢复。
另查看[Cranston–Rabern, Beyond Degree Choosability](https://arxiv.org/html/1511.00350)
引言及Theorem A作为Gallai树背景；T037本身用初等三角形恒等式证明，
不依赖未完整读取的分类定理。

本轮历史恢复：`references/history/`新增原样历史总账、finite-Abelian
及mature-reducibility报告，SHA256纳入现行检查。原五/六/七轨道ZIP
均未恢复；T033及T036是新生成证书，不是给历史计算标签自动升级。

- Landon Rabern, [A different short proof of Brooks' theorem, v5](https://arxiv.org/html/1205.3253)：
  本轮已读ordinary版本及Theorem2列表版本和证明。T034使用
  χ_l≤max{3,ω,Δ}，不能以ordinary三色性替代非均匀名单延伸。
- Atserias–Kolaitis, [Consistency, Acyclicity, and Positive Semirings](https://arxiv.org/abs/2009.09488)：
  本轮核验摘要入口，作为布尔/概率关系连接的背景；没有宣称全文重读，
  新T032–T036不依赖其未读取正文定理。

## 容易误读的地方

2026-09-09新增pair-interface参考：
`/Users/fire/Downloads/Hadwiger_Nelson_pair_interface_generalization_5_6_framework_2026-09-09.md`，
全文1284行已读，SHA256为
`c4bf9b8f20deb8de5b8e5f603003b4938b8720af736b6765cbda382cbe714f7f`。
原文件未修改；作为参考而非路线指令。自主评价、基础重证、优先级
差异及非声明见`docs/proofs/pair_framework_priority_v4.md`。

- [Bonamy–Kang, List colouring with a bounded palette, v2](https://arxiv.org/html/1507.03495v2)：
  已读引言、§2定义/Proposition6/Theorem7及相关说明。特别核对
  每个二分图均(r,2r−2)-choosable；T055为直接调色板分割应用，
  不是新列表染色定理。未把一般高choice number当作非(4,6)的证据。
- [Keith Conrad, On Weil's proof of the bound for Kloosterman sums](https://kconrad.math.uconn.edu/articles/kloosterman.pdf)：
  原PDF文本编码乱码，已渲染直接核对第1、4、5页，使用Theorem3的
  未扭曲Kloosterman界2√q；没有重证其Riemann hypothesis输入。
  缓存`references/cache/conrad_kloosterman.pdf`，SHA256为
  `045967ea63a4fefa99a910c2061b0f7dfc5dfe61fced18a5759b37466858d780`。
  只读PDF采用本地可选PyMuPDF 1.26.7渲染；不属于`make check`依赖。
- [Vinh, math/0510092v1](https://arxiv.org/html/math/0510092)：
  本轮直接检查正文Lemma4/§3，其√q常数与摘要1/2渐近系数不一致；
  T053不依赖这处所印强界，而从Weil界独立推导安全的2√q谱界。
  本地对F11/F131的17280频率做整系数恒等式校准，非浮点谱估计。

本轮框架参考全文2213行已读，未作为强制路线。新增外部核验：

- [Madore, §5.4](https://arxiv.org/html/1509.07023)：重新阅读实闭域转移，
  `χ(R²)=χ(A²)`（A为实代数数）是外部成熟结论；本轮重述有限配置
  保留互异与非边的公式，不将它登记为新的本地发现。
- [Loh–Sudakov, Independent transversals in locally sparse graphs](https://arxiv.org/html/0706.2124)：
  已核对引言及Theorem1.1，局部度界不替代全局Δ与分块大小条件；
  不能由14端口/局部度2直接增强T042，也不能省掉T043负约束。
- [Atserias–Kolaitis](https://arxiv.org/html/2009.09488)：本轮进一步阅读
  §§4.1–4.3的running-intersection、join-tree与关系/概率一致性定理，
  用于框架重审；不将仅单点边际一致当作全局染色证据。
- [Sokolov–Voronov, On the chromatic number of the plane for map-type colorings](https://arxiv.org/abs/2502.01958)：
  只核对摘要中的map-type与边界附加条件；其七色结果不适用于任意
  普通平面染色，未重放全文证明。

本轮Property-B资产：完整阅读Downloads中的
`HN_round_conclusions_propertyB_repair_cascade_2026-09-08 (1).md`；
参考但不作为路线指令，未为归档完整性重复复制历史文件。

- Grill–Linzmayer, [Improved Lower Bounds for Property B, v3](https://arxiv.org/html/2403.05674v3)：
  已读§§1–3及Theorem 1，m(7)≥128按外部定理使用；没有独立重放其
  GMP计算。这给T039单颜色修复127条不同超边的充分界，不是新HN界。
- Moser–Tardos, [A constructive proof of the general Lovász Local Lemma, v3](https://arxiv.org/html/0903.0544v3)：
  已读§1及Theorems 1.1/1.2；D≤22以x=1/23的精确有理不等式校准。
  不宣称本文后续算法分析已全部独立重证。

1. 局部满射(每邻域看到其余全部色)并不等于equitable(颜色级邻数固定)。
2. 7色 affine 三角格覆盖不是全平面7色铺砌本身。
3. 普通单位距离图允许边交叉；若“planar gadget”指平面图，会被四色定理
   限制。本文统一用“二维单位距离实现”。
4. escape state 的凸包不自动是某既定多面体的face；使用face术语要给支持超平面。
5. 临界feasible face技术可借鉴，但普通fractional chromatic有<4.36的上界，
   无法单凭普通χ_f>5推进到六色下界。
