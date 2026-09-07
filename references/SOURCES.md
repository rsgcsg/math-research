# 外部资料与历史输入

检查日期：2026-09-08。原论文结论、作者的计算声明、本地独立验证分别记录。
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
| Haugland v4 (2026) | https://arxiv.org/html/2608.04542v4 | 正文核验740点 DIFF4(sqrt3) 到2131点构造；509仍是文中纪录。不是无spindle最小纪录，已有1441点 |
| Matolcsi et al. | https://arxiv.org/abs/2311.10069 | geometric fractional 与27点系统；需区别普通 χ_f |
| Dúcz (2026) | https://arxiv.org/html/2606.12325v1 | 已读4色公式与模4证明；Moser lattice/ring 确有普通4染色 |
| Dúcz–Varga (2026) | https://arxiv.org/html/2606.28157v1 | 原文确认29点 geometric fractional >4.0007；两新点在普通图只是叶子。全等约束与blow-up不可省略；原始LP证书尚未本地重放 |
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

## 容易误读的地方

1. 局部满射(每邻域看到其余全部色)并不等于equitable(颜色级邻数固定)。
2. 7色 affine 三角格覆盖不是全平面7色铺砌本身。
3. 普通单位距离图允许边交叉；若“planar gadget”指平面图，会被四色定理
   限制。本文统一用“二维单位距离实现”。
4. escape state 的凸包不自动是某既定多面体的face；使用face术语要给支持超平面。
5. 临界feasible face技术可借鉴，但普通fractional chromatic有<4.36的上界，
   无法单凭普通χ_f>5推进到六色下界。
