# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**本项目尚未改变5≤χ(R²)≤7。**
[当前状态](docs/CURRENT.md) · [结果账本](docs/RESULTS.md) · [路线与淘汰理由](docs/ROUTES.md) ·
[统一框架](docs/proofs/hn_unified_framework.md) · [文献地图](references/LITERATURE_MAP.md) · [证据规则](AGENTS.md)。

## 2026-09-28：原Y内循环边际的精确答案，T143/E114/C026

五点事件的η闭包只有11点且全部在原Y；三个模式概率的精确k≥3可行域为
`([0,1]^3+conv(0,e0,e1,e2))/5`，13个顶点均由真实三色旋转律实现。
原Y完整η约束已排除上轮C025三原子边际，无须为这条4/5界新增30点。
122位置传播的计数最优98亦三色可达；全Y正词让该观察族的完整五点划分全部恒定，
因此继续只在这个族内调势无效。联合位置产生真实相关差，整体核观察的单词有独立RUP反证，
随后五词混合已正解决该28项F共同律，且是五原子极点；原Y全15域仍未判定。
[完整证明与实验](docs/proofs/original_Y_cycle_descent.md) · [有限证书](certificates/original_Y_cycle_descent.json) ·
[单词反证](certificates/joined_kernel_singleton.json.gz) · [五词共同正律](certificates/joined_kernel_five_law.json)。

## 已继承的最近成果

T138整个双旋转宿主恰五色；T139有限秩平移接触分类；远端T140有效单旋转平移子类。
T141六完整域最小支持恰2；C025局部三原子极点不属于两词包凸包；T142真实五阶循环延拓界。
这些结论均保留原范围。原来的UNKNOWN不因为后续受限反证而改写。
[两词及29点核心](docs/proofs/two_atom_motion_packet.md) · [局部极点与86点循环](docs/proofs/cyclic_pattern_extension.md) ·
[单旋转平移](docs/proofs/cyclic_translate_effective.md) · [有限几何构造入口](docs/proofs/next_attack_gate.md)。

## 重放

```sh
make check                       # 全部标准库独立检查，不是新的昂贵搜索
make check-cycle-descent         # 本轮完整Y重建、循环多面体、零词、联合核RUP与篡改
python3 -S research/verify_cycle_descent.py
python3 -S research/verify_joined_kernel.py
```

研究基准为本地b532e714，保留远端09926d59的真实祖先。完整基线与新增入口的实际验证范围
见[本轮收据](certificates/cycle_descent_validation.json)。分阶段覆盖不冒称最终树单次全量运行。
一般数学命题依赖完整证明，不因检查器通过就成为已形式化或同行评审结果。
当前连接未提供写入动作，新提交及上轮未发布成果保存在本地Git与累计补丁，不冒称远端main已更新。
历史归档恢复说明见[BRANCHES](docs/BRANCHES.md)。
