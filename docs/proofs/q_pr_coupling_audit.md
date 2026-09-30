# E119: bounded Q/P/R coupling audit

**Scope:** an exact combinatorial audit of the already certified selected pair components on the fixed set `Y`. This closes only the examined ordinary pair-path and alpha-at-most-2 matching refinements. It is not a full Q-augmented BW proof, a full15 result, or an HN bound.

## Pinned inputs and source results

The verifier uses the actual unit-edge set `E` and the certified selected pair sets:

- `P`: 1,860 pairs from the squared-distance-`1/3` transport component
- `Q`: 780 pairs from the selected squared-distance-`4` component
- `R`: 1,472 pairs from the selected squared-distance-`4/3` component

The geometry has 10,077 vertices and 49,858 actual unit edges. Its semantic geometry hash is `90674956a11ac0b6627fb12c6bc108f1c4ddf2ca037c39a9271cf6ba896c0957`; the P/Q basis hash is `757a6f62edfb5285b9fde82f55c93454abd6e6a5b1985f3838d4c2a93e003534`; the R candidate hash is `f21599cb3ed6076e797f1fed319d5e8d4941c50b05fdaed12c6de218a6e9c976`.

The P/Q source and exact one-word witness are covered by [T155](g14_selected_pair_orbit_law.md); the P/R pair component and support-independent face bound are covered by [T157](g14_pr_transport_bound.md). The starting P/R polygon is [T158](nine_point_pr_polygon.md); the existing alpha-at-most-2 P/R census is [T158(b)](pr_matching_window_ceiling.md). The matching-cut calibration is [C027](matching_partition_family.md), and the known-node E/P/R BW family is [T159](bw_pr_odd_cycle_ceiling.md). The verifier reuses `verify_pr_matching_window_ceiling.validate_inputs` and its two clique enumeration helpers; it separately pins and checks the P/Q basis hash.

## Exact quotient counts

Contracting the selected Q pairs gives 9,577 equivalence classes (500 merges), with class-size histogram `{1: 9359, 3: 158, 4: 58, 6: 2}`. No actual unit edge becomes a loop. No selected P or R event collapses inside one Q class. The quotient-pair edge counts are 48,706 for E, 780 for P, and 332 for R; the P/R, P/E, and R/E quotient-pair intersections are all empty. Thus Q-only contraction does not directly force a P/R event equal or different through a unit contact.

Contracting Q together with all R pairs gives 9,341 classes. It creates 120 actual E loops. A separate 188 selected P pairs become loops only when their required difference `p=0` is also imposed. Hence the old combined count is **120 E loops + 188 P conflicts = 308 conflicts**, not 308 unit loops. Independently checked short witnesses are:

- actual unit edge `{238,305}`, closed by R equal-pair path `{238,229}`, `{229,4641}`, `{4641,305}`
- selected P pair `{229,305}`, collapsed by R path `{229,4641}`, `{4641,305}`

The first path has three R steps; the second gives `2r-p <= 1`, already one of T157's inequalities.

On the Q quotient graph whose edges are selected R pairs, the exact shortest-distance censuses are:

- endpoints of actual E pairs: R-distance 3 for 72 pairs, 4 for 48 pairs, and disconnected for 49,738 pairs; none has R-distance 1 or 2
- endpoints of selected P pairs: R-distance 2 for 76 pairs, 3 for 64, 4 for 48, and disconnected for 1,672; none has R-distance 1

Distances are shortest numbers of R edges **after contracting the entire Q component**, so longer Q paths cannot hide a shorter-R obstruction. Consequently, an E-closed path using only R steps needs at least three R mismatches, automatic on H since `r <= 3/5`. A P endpoint path with two R steps yields only `2r-p <= 1`; paths with at least three R steps are automatic on H. Direct quotient overlaps that could give a one-step cross-component P/R path are absent.

## Ordinary pair-path cuts: complete scope argument

For a path of known pair events from `v0` to `vm`, close it by the known pair `{v0,vm}`. Let `e_i` be the same-color indicator of path pair `i`, and `e_close` the closing-pair indicator. For every partition,

`sum_i e_i - e_close <= m-1`.

If any path edge is an actual E edge, its equality indicator is zero; all other path indicators are at most one, and the closing mean is nonnegative. The cut is then automatic. It remains to consider paths using only P/Q/R pairs.

Write `a` for the number of Q steps and `L` for the number of P/R steps in the path. The means on P/R lie in H, so `max(p,r) <= 3/5`.

- **Closing by E:** `a q + sum(P/R) <= a+L-1`. The worst case is `q=1`. If `L>=3`, `sum(P/R) <= 3L/5 <= L-1`. If `L=2`, the only potentially sharp case is R/R, but the unit-endpoint R-distance census excludes it; P/P and P/R are slack on H. If `L=1`, a nontrivial E/event quotient overlap would be required, and all such overlaps are empty. If `L=0`, there is no Q-only unit loop.
- **Closing by P or R:** subtract the closing mean from `a q + sum(P/R)`. The worst case is again `q=1`. For `L>=3`, the bound `3L/5 <= L-1` applies. For `L=2`, the only nontrivial case is an R/R path closed by P, giving the existing `2r-p <= 1`; all other P/P and P/R closures are automatic on H. For `L=1`, same-component closures are tautological because both means are the same variable; a nontrivial cross-component or event/E contact would require a quotient-pair overlap, which is absent. For `L=0`, Q-only P/R collapses are absent.
- **Closing by Q:** the cut is `(a-1)q + sum(P/R) <= a+L-1`. If `a>=1`, its left side is largest at `q=1`, where `sum(P/R)<=L` makes the cut automatic. If `a=0`, then `L>=3` is automatic from `sum(P/R)<=3L/5<=L-1`; at `L=2`, R/R gives the one additional triangle bound `2r-q<=1`, while P/P and P/R are automatic on H; at `L=1`, the path would collapse a P or R pair inside one Q class, and no such quotient loop exists.

Therefore the ordinary known-pair path family considered here leaves every point of H available at `q=1`. This is a projection statement about necessary inequalities, not a claim that an actual full-Y law exists at `q=1`.

## C027 matching-window applicability

On the fixed support graph `E union P union Q union R`, the verifier enumerates all five-cliques in two independent ways: ordered common-neighbor recursion, and pivoting Bron-Kerbosch followed by deduplicated subsets. Both produce 11,160 five-cliques. Filtering for alpha(`E[W]`) at most 2 leaves 2,280 windows, all with four P pairs, zero Q pairs, and two R pairs. Each nonunit graph is exactly `K_{2,3}`, hence bipartite; the matching bound `4p+2r <= 2`, or `2p+r <= 1`, is already a facet of H. There is no Q-containing C027 C5 blossom window. By five-subwindow heredity, no larger alpha-at-most-2 matching window of this support can contain Q either.

For alpha-at-most-2 windows of size 3 or 4, the matching-cardinality lower bound for at most five blocks is vacuous. A nontrivial vertex-degree cut involving a Q edge would require two nonunit pairs sharing a vertex and the opposite pair to be an actual E edge. Q contraction would then create a Q-only E loop or a P/E or R/E quotient-pair overlap, all excluded above. If the opposite pair is another nonunit event edge, the three vertices have no E edge and the window has alpha at least 3, outside the matching family. Thus the smaller-window degree and odd-set cuts add no Q restriction either.

## Selected triangles and the single-independent-set relaxation

A full exact census of triangles in the certified selected P/Q/R pair-event graph gives:

| Pair types | Count |
|---|---:|
| PPP | 1,080 |
| PPR | 1,380 |
| PRR | 68 |
| QQQ | 280 |
| QRR | 1,560 |
| RRR | 720 |

No PPQ, PQQ, PQR, or QQR triangle occurs. The exact QRR witness on vertices `31,35,873` has R pairs `{31,35}`, `{31,873}` and Q pair `{35,873}`. Transitivity gives the genuine Q/R marginal coupling

`2r-q <= 1`, equivalently `q >= 2r-1`.

This is only the ordinary three-point triangle inequality, which remains inside the globally feasible single-independent-set moment relaxation. For binary independent-set indicators X,

`X31*X35 + X31*X873 - X35*X873 <= X31`

holds pointwise; the verifier checks all eight binary assignments. Thus the coupling does not supply a partition-specific cut beyond that relaxation.

## Conclusion and limits

The certified Q component adds an ordinary QRR triangle coupling, but no stronger partition-specific odd-set cut in the inspected alpha-at-most-2 family. Q-contracted ordinary pair-path checks do not shrink H at `q=1`. Retire these bounded metric/path and C027 matching refinements; do not generalize that retirement to every Q-based approach. The full Q-augmented BW auxiliary-graph family, unknown-coordinate cancellation combinations, higher-order partition cuts, alpha-at-least-3 windows, and full15 feasibility remain untested.

Replay with `make check-q-pr-coupling-audit`. The standard-library checker is `research/verify_q_pr_coupling_audit.py`; default mode compares `certificates/q_pr_coupling_audit.json`, and `--write` explicitly regenerates it. The target depends on the established P/R local projection checks and the exact selected-pair transport check.
