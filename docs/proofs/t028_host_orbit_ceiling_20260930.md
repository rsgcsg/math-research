# T028 safe-host terminal relation

**T153.** This is a finite-table audit and a consequence of the existing T028 proof. It
is **not** a new Hadwiger–Nelson lower bound and does not color the Euclidean
plane. It gives a useful obstruction to gadget searches when every gadget
vertex stays in the exact host
`K^2`, where `K = Q(sqrt(3),sqrt(5),sqrt(11))` in its usual real embedding.

## Host-orbit principle

Let `X` be a point set whose graph edges are preserved by a family of valid
host colorings. If one such coloring realizes a terminal color-equality
pattern on a tuple `s`, every symmetry-orbit image `t` of `s` realizes the
same pattern by pulling back the coloring. More generally, if a transformation
of the finite quotient graph preserves its edges, precomposing the quotient
coloring with that transformation gives another valid host coloring. Any
finite gadget contained in `X` inherits these colorings by restriction. Thus
one witnessed terminal pattern is enough to show that a free gadget inside
`X` cannot forbid it. This is a one-way obstruction principle; it does not
assert that the exhibited host-coloring family is the complete set of all
colorings of every finite gadget.

The host distinction matters: the results below concern actual finite
unit-distance subgraphs embedded in `K^2`. They say nothing about a quotient
graph being a Euclidean-plane graph, and do not apply to gadgets with vertices
outside `K^2`.

## T028 dependency

The existing [T028 proof](residue_field_ceiling.md) establishes that the full
graph on `K^2`, with every actual Euclidean unit pair as an edge and arbitrary
`K` denominators, is 5-colorable. It follows the established valuation
reduction in Madore, *The Hadwiger–Nelson problem over certain fields*,
Proposition 3.2 / Corollary 3.4: embed `K` in
`Q_11(sqrt(11))`, whose valuation ring has residue field `F_11`; anisotropy
of `x^2+y^2` over `F_11` forces every unit direction into the valuation ring;
every unit edge stays within one additive valuation-ring coset; reduce each
coset to the verified five-coloring of `F_11^2`. The full T028 proof supplies
the Hensel, valuation, arbitrary-denominator, and exact-scope details. Primary
source: <https://arxiv.org/abs/1509.07023>. No coloring of `R^2` is claimed.

The table [`residue11_coloring.json`](../../certificates/residue11_coloring.json) has 121 points
indexed by `(x,y) in F_11^2`, color `rows[x][y]`, and 726 norm-one edges.
The independent checker exhaustively finds these same-color / different-
color unordered-pair counts by residue norm:

| Norm | Same color | Different colors |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 0 | 726 |
| 2 | 281 | 445 |
| 3 | 231 | 495 |
| 4 | 152 | 574 |
| 5 | 96 | 630 |
| 6 | 183 | 543 |
| 7 | 134 | 592 |
| 8 | 172 | 554 |
| 9 | 88 | 638 |
| 10 | 76 | 650 |

For norm 0, no distinct points occur because `-1` is nonsquare and the norm
form is anisotropic. Norm 1 is exactly the finite unit-edge relation. Thus
both color-equality statuses are present for every residue norm `2,...,10`.
Concrete equal-color pairs based at `(0,0)` for the nonzero square norms
relevant to ordinary real lengths in `K` are `(0,6)` at norm 3, `(1,5)` at
norm 4, `(0,4)` at norm 5, and `(2,4)` at norm 9; each endpoint and origin
has table color 0.

## Whole-host two-terminal relation

The relevant transformations need not be geometric isometries of `K^2`.
Within one additive coset `z+A^2`, choose any `M in O_2(F_11)`, any
`b in F_11^2`, and any permutation of the five color names, then color a point
`p` by applying that palette permutation to

`phi(M rho(p-z) + b)`,

where `rho : A^2 -> F_11^2` is the T028 reduction and `phi` is the table. This
is still proper: each actual unit edge lies in one such coset, its reduced
difference has norm one, and `M` preserves the norm; `b` cancels in a
difference. Cosets can be colored independently because there are no unit
edges between them.

For each `r != 0`, `O_2(F_11)` acts transitively on vectors of norm `r`. One
short proof identifies `F_11^2` with `F_121` using `i^2=-1`; the norm is the
field norm. Given nonzero `u,v` with equal norm, `v/u` has norm one, so
multiplication by `v/u` is an orthogonal map carrying `u` to `v`. An
exhaustive check in the accompanying script independently confirms 24
orthogonal matrices and transitivity on all ten nonzero shells.

Now fix any two terminals in the same `A^2` coset whose reduced displacement
has norm `r in {2,...,10}`. For either desired equality status, take a table
pair at norm `r` with that status, use an orthogonal map to match its
displacement to the target, then use `b` to align the first terminal's
reduced position. A palette permutation gives any desired named pair of
colors with that equality status. Hence the T028 host admits all 25 ordered
two-color assignments on such a pair. No finite free 5-coloring gadget wholly
inside `K^2` can force either equality or inequality on that terminal pair.

For terminals in different `A^2` cosets, independent palette permutations
also realize any of the 25 ordered color assignments. For terminals in one
coset with equal reductions (norm zero), this particular quotient-coloring
family realizes equality. With reduced displacement norm one, it realizes
inequality; if their actual distance is one, that inequality is in addition
forced by the actual unit edge. These statements only describe witnessed
colorings; do not infer an unproved exact characterization of the full
finite-gadget relation for norm-zero or non-edge norm-one pairs.

For the two candidate distances `2` and `1/sqrt(3)`, the squared-distance
residue is 4, since `1/3 = 4 mod 11`; both are in the norm-4 two-terminal
regime. In particular, no free disequality gadget at either separation can
live wholly inside `K^2`. This does not prevent gadgets escaping `K^2`, and
does not preserve an externally imposed precoloring or boundary assignment.

## Reproducibility and provenance

Run the standard-library-only finite checker from the repository root:

```sh
python3 -S research/verify_t028_host_orbit_ceiling.py
```

It verifies the table SHA256, every finite norm-one edge, both complete
same/different norm-residue censuses, and orthogonal-group shell transitivity.
It does not certify the infinite valuation argument; that is the cited T028
dependency.

The original source checkout HEAD was
`b87a0d7a5dc62a4e13c2411ed09e2c162a36c664`; this extension is recorded on the
published `main` base `1bf57231b05730364372136c065e4f25bf3fdbef`. T028's proof,
finite table, and verifier were last changed in commit
`cb8d1cfd993220e9af607683f683ef268e987bca`. Their exact hashes were rechecked
unchanged in the published base:

* `docs/proofs/residue_field_ceiling.md`:
  `a788e5af820089f035e0a00a3e0c6a89463d0809c0cbc8a30ac261d90de4d429`
* `certificates/residue11_coloring.json`:
  `ae2fc6b4d66911ce16cc5bafc5199836ae8745e0c53e76249060417a01485d7c`
* `research/verify_residue11.py`:
  `94b133b3bb77f227adee79f71ce7ec6c0310100dc611c6635b1bd0fcdd1645bb`

The residue-field method is attributed to Madore. This note makes no
priority, novelty, or new HN-bound claim.
