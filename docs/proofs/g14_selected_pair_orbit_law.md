# T155: G14 selected pair-orbit witness: quotient principle and exact scope

Review date: 2026-09-30  
Status: independently checked finite certificate; no HN or full15 claim.

## Claim proved by this certificate

Let `Y` be the finite point set encoded by the checked geometry. It has `n = 10,077` vertices and its induced unit-distance graph has `49,858` actual edges. Let

- `A` be the `1,860` selected unordered pairs in the single pair-event orbit seeded at squared distance `1/3` by the G14 virtual-pair certificate, closed under the 15 listed partial motions and their inverses
- `B` be the `780` selected unordered pairs in the corresponding orbit seeded at squared distance `4`
- `E` be **all** actual unit-distance edges of `Y`

There is a verified map `c : Y -> {0,1,2,3,4}` such that

- `c(x) != c(y)` for every `{x,y} in E union A`
- `c(x) == c(y)` for every `{x,y} in B`

The checker recomputes the exact squared distances of every selected pair in the specified 32-coefficient algebraic representation, checks every actual unit edge, and checks the actual witness word. The pair-event values are therefore constant on each selected orbit component: all 1,860 `A` events are false for equality, and all 780 `B` events are true for equality.

This is an exact, finite constraint-satisfaction witness. It does not assert that `A` or `B` contains every pair in `Y` of the same metric distance. It does not give a full pair-pattern law for any original 15-domain, a coloring of the plane, or a Hadwiger–Nelson bound.

## Structural principle: contract equalities, color the quotient

For any finite vertex set `V`, let `R_eq` and `R_neq` be sets of required-equal and required-different unordered pairs. Let `~` be the least equivalence relation containing `R_eq`. Form the quotient graph `H` as follows:

1. vertices of `H` are the `~`-classes in `V`
2. for each `{x,y} in R_neq`, add an edge between `[x]` and `[y]`
3. a pair with `[x] = [y]` creates a loop and certifies infeasibility

Then a coloring `c:V -> {1,...,k}` satisfying all equalities and inequalities exists **iff** the loop-free quotient graph `H` is properly `k`-colorable. In one direction, each equality class receives one color, so `c` descends to `H`; in the other direction, pull a proper coloring of `H` back along the quotient map. This is a direct finite equivalence, not a new coloring theorem.

For this witness take `R_eq = B` and `R_neq = E union A`. Union-find gives `9,577` quotient vertices from the original `10,077` vertices. The 780 equality pairs induce 500 net vertex merges; the equality-edge graph has 280 cycle-rank redundancies. No required-different pair becomes a loop. After deduplicating quotient edges, `E` contributes 48,706 edges, `A` contributes 780 more, and their overlap is empty, for `49,486` conflict edges total. Pulling the checked word to the quotient gives a proper 5-coloring. The class color counts are `1,994, 1,958, 1,872, 1,918, 1,835` (labels 0 through 4), so all five labels occur. These are witness statistics; no minimal chromatic number is claimed.

This quotient graph is the simple structural reading of the SAT instance. The original 10,077-vertex, 5-label CNF has 50,385 Boolean variables and 377,237 clauses. The CNF/hash is useful provenance, but the proof of satisfiability is the direct finite word plus independent checks, not trust in the SAT solver.

## Pair-orbit closure and the important boundary

The G14 certificate contributes 27 `1/sqrt(3)` seed events and 5 `2` seed events. Replaying the actual pair maps and inverses gives one connected component per grade: respectively 1,860 and 780 pair-nodes, with 14,248 actual pair-map transitions checked. The saved basis has 1,859 and 779 rows. The hardened review checker separately verifies that those rows themselves are simple spanning trees, not merely that the full orbit graphs are connected.

For a deterministic partition `Pi` of `V`, the partition induced on a domain is determined exactly by all pair indicators `1[x ~ y]`. Thus, for a partial bijection `f:D -> R`, preservation of **every** pair-equality indicator on `D` is equivalent to equality of the two induced partitions on `D` and the pullback along `f` of the partition on `R`. Under a Dirac law, each pair-event expectation is already a zero-or-one value, so balancing all pair events forces this full pattern equality.

For a mixture of partitions, balancing pair-event expectations only matches pairwise marginals; it does not determine the distribution of complete patterns. For example on three points, (i) a uniform choice among the three partitions with exactly one equal pair and (ii) a law assigning probability `1/6` each to the all-equal partition and each one-pair partition, plus probability `1/3` to the all-distinct partition, both give each pair equality probability `1/3` but are different laws.

The current witness checks only the two selected pair-event components `A` and `B`. It does **not** check all pair events in any of the original 15 domains. In fact, the checked coloring fails full-domain pair invariance for every one of the 15 motions. The following table gives one verified counterexample per motion; braces denote unordered pairs and `=`/`!=` indicate whether the two endpoint colors agree:

| motion | source pair -> image pair | source -> image equality status |
|---|---|---|
| tau | {31,32} -> {6268,6269} | `=` -> `!=` |
| nu | {4,5} -> {22,23} | `=` -> `!=` |
| eta | {0,3} -> {8080,8173} | `!=` -> `=` |
| omega | {4,5} -> {9919,9920} | `=` -> `!=` |
| bar | {31,32} -> {38,8149} | `=` -> `!=` |
| bridge | {32,165} -> {9063,9071} | `!=` -> `=` |
| translation_one | {32,122} -> {876,1772} | `=` -> `!=` |
| translation_z | {230,481} -> {32,122} | `!=` -> `=` |
| one_plus_eta_1 | {231,704} -> {5173,7203} | `=` -> `!=` |
| one_plus_eta_2 | {232,3533} -> {231,3503} | `!=` -> `=` |
| one_plus_eta_3 | {232,467} -> {7468,8158} | `=` -> `!=` |
| one_plus_eta_4 | {31,121} -> {237,488} | `=` -> `!=` |
| bridge_shift | {231,3533} -> {3666,8562} | `=` -> `!=` |
| minus_bar | {31,32} -> {475,9755} | `=` -> `!=` |
| dyadic_u | {233,239} -> {238,5557} | `!=` -> `=` |

Accordingly, the finite quotient coloring is a witness for a **selected** deterministic pair-event face, not a quotient solution for a full-domain deterministic G14 pattern. An assignment of arbitrary 0/1 values to all pair events would also not suffice by itself: to represent colors or a partition, the equality relation must be transitive and the inequality constraints must remain proper after contraction.

## Does this reveal a finite-field/residue coloring?

No finite-field or residue formula is established by these files. The output is a concrete SAT-produced coloring of a particular finite algebraic point set and a resulting finite quotient graph. The checked certificate supplies a word, not a formula assigning labels as a residue of coordinates. No claim that the witness is a known finite-field coloring is justified here. A future search could ask whether the quotient coloring admits a simpler algebraic description, but that would be a separate result; this check does not exclude nonlinear or differently encoded residue models.

## Verification and provenance notes

- The solver-free checker rebuilds the CNF independently and matches its SHA256 and clause count, but the witness proof is the direct word check.
- The exact input semantic geometry hash is `90674956a11ac0b6627fb12c6bc108f1c4ddf2ca037c39a9271cf6ba896c0957`.
- The pair-orbit forest-basis hash is `757a6f62edfb5285b9fde82f55c93454abd6e6a5b1985f3838d4c2a93e003534`.
- The SAT-word SHA256 is `39fa668004a67780783dc099b48382f6879980f7a72986712d3133dbb0656cb3`.
- The historical G14 source certificate SHA256 is `a31795df303c8dd3ff0719ab0d2ea470c28913f1c814c7e1fd29cfee1ee1f896`. Separately rerunning `verify_g14_port_or.verify(...)` on the saved Parts509 core and geometry exactly reproduced the stored certificate, including 27 + 5 virtual pair events.
- Original checker's forest-row count and per-row transport checks did not themselves establish no duplicates/cycles or forest connectivity. The published checker adds those independent structural checks and passed baseline plus the duplicate, cycle, and disconnect mutations implemented in `research/test_g14_pair_orbit_forest.py`.

## Portable replay

`make check-g14-pair-orbit` reconstructs audited geometry, checks the positive word, complete pair closures, forest rank, quotient counts and one counterexample per full domain, then runs forest mutation tests. The independent checker is `research/verify_g14_pair_orbit_law.py`; its default mode compares `certificates/g14_pair_orbit_verification.json` rather than overwriting it.

The frozen basis is `certificates/g14_pair_orbit_basis.json.gz`; the word is `certificates/g14_pair_orbit_word.json`. The search used a G14 certificate predating an added geometry semantic-hash field. The checker verifies that field against reconstructed geometry, removes only that metadata field from a copy, and reconstructs the old exact bytes to preserve the frozen basis identity. Both hashes and this migration are recorded in the receipt. No geometric or combinatorial data are changed.
