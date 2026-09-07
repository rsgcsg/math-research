# Hadwiger-Nelson: extension barriers, list-pressure geometry, and exact cross-copy searches

Date: 2026-09-07. Incremental research record.

**Status.** This work does not establish a six-chromatic unit-distance graph, a six-coloring of the whole plane, or the exact chromatic number of the plane. It establishes the elementary extension results proved below and checks specific finite searches. No literature-priority claim is made for these deductions.

## 1. What was carried forward and what was actually rechecked

The immediately preceding record was `HN_R4_audit_and_cross_lattice_research_2026-09-07.md`, with its exact certificate package. Its standard-library verifier was run again successfully. This covers the R4 conditional contradiction, the 56-point/31-domain inclusion-minimal conditional core, the denominator-9 probability witness, the integer Farkas certificate, and the 3440-event unconditional escape inequality. These remain statements about their specified conditional systems and probability models, not six-chromatic graphs.

This run then left the aligned R4 system and investigated real cross-lattice and cross-copy geometry. Coordinates and all unit edges, including accidental ones, are retained exactly. Search timeouts are never interpreted as non-colorability.

The public construction used as a calibration and seed is de Grey, *The chromatic number of the plane is at least 5*, arXiv:1804.02385v3, Section 5.1. Its 39 representative coordinates and prescribed isometries were reconstructed independently in this run. Its published non-four-colorability result is used as an external theorem; no new non-four-colorability proof of that construction is claimed.

## 2. Definitions

Let omega = (1/2, sqrt(3)/2), and let Lambda = Z(1,0) + Z omega. A unit triangular lattice is any translate and orthogonal image of Lambda, with spacing exactly one. Scaling the lattice to another spacing is not allowed in the results below.

A faithful unit graph on a point set includes every pair at Euclidean distance exactly one. Edges are allowed to cross.

A finite graph is d-degenerate if every nonempty induced subgraph contains a vertex of degree at most d. Repeated deletion of such vertices, followed by reverse-order greedy coloring, proves that a d-degenerate graph is (d+1)-choosable: it can be colored even if every vertex has its own list of d+1 allowed colors.

## 3. The external-neighbor lemma

**Lemma 1.** If x is not in a unit triangular lattice Lambda, then x has at most one unit-distance neighbor in Lambda.

**Proof.** Suppose p and q are distinct lattice points at distance one from x. Then 0 < |p-q| <= 2. Write q-p = a+b omega. Its squared length is the integer a^2+ab+b^2. The only positive values at most four are 1, 3, and 4. Up to a symmetry of Lambda, the displacement is respectively 1, 1+omega, or 2.

For displacement 1, the two intersections of the unit circles about 0 and 1 are omega and 1-omega, both lattice points. For displacement 1+omega, the intersections are 1 and omega. For displacement 2, the unique intersection is 1. Translation and lattice symmetry therefore put x in Lambda, a contradiction. QED.

The verifier enumerates all 18 nonzero lattice displacement vectors of length at most two and checks their one or two lattice circle intersections. This finite check supports the proof; the classification and two-circle geometry make the statement apply to every external real point.

**Consequences.** Between the exclusive parts of two triangular lattices, the cross-unit edges form a matching. A common lattice point is an exception to that matching description: it is not external to either lattice and can have many neighbors. The subsequent theorem handles common points explicitly.

## 4. Two arbitrary triangular lattices are five-choosable

**Lemma 2.** Every finite induced subgraph of a unit triangular lattice is 3-degenerate.

**Proof.** Choose a generic linear functional with a unique maximum on the given finite set and nonzero value on each of the six unit directions. At its maximum, only the three decreasing unit directions can lead to other vertices. Apply this to every remaining subset. QED.

**Theorem 3.** Every finite unit graph contained in the union of two arbitrary unit triangular lattices is 4-degenerate, hence 5-choosable. In particular, the entire union is five-colorable.

**Proof.** Let the finite point set be P. Put A=P intersect Lambda_1 and B=P minus Lambda_1; thus B is contained in Lambda_2. Each vertex of B has at most one neighbor in A, by Lemma 1. Repeatedly choose a degree-at-most-three vertex of the remaining B using Lemma 2. Its degree in the remaining full graph is at most four. Once B is deleted, the remaining A is 3-degenerate. This gives a 4-degeneracy order for P. Compactness extends five-colorability to the full, countable union. QED.

No assumption is made that the lattices are disjoint, share only one point, have rational angles, or have a small number of cross edges.

**Theorem 4 (relative extension).** Every proper coloring of the whole Lambda_1 with a fixed five-color palette extends to a proper coloring of Lambda_1 union Lambda_2 with that same palette.

**Proof.** At each vertex of Lambda_2 minus Lambda_1, the fixed first-lattice coloring forbids at most one color. Its remaining list has at least four colors. Every finite subgraph of the second exclusive part is 3-degenerate and therefore colorable from those lists. Compactness gives the extension. Common points retain their already fixed colors. QED.

This is stronger than merely asserting that some five-coloring exists.

### Convex precoloring corollary

Let H be a finite lattice-convex patch of Lambda_1: every lattice point in its convex hull is already in H. Every proper coloring of H with at least four colors extends to Lambda_1.

For a finite extension, separate an outside point from conv(H) by a linear functional and take a generic maximum outside H. It has at most three neighbors in the remaining finite graph. Delete such points until only H remains and color in reverse. Then use compactness.

The regular seven-point wheel is lattice-convex. Thus every one of its 31 oriented five-color partitions extends to the union of any two unit triangular lattices containing that wheel. Consequently, a construction confined to two such lattices cannot provide a nontrivial single-wheel five-color filter at that wheel.

This does not assert that arbitrary precolorings of arbitrary non-convex finite first-layer patches extend; precolored holes can cause additional constraints.

### More than two lattices

For a cover by r triangular lattices, partition vertices by their first containing lattice. Remove the highest-index part first. Each point in that part is external to every earlier lattice, so it has at most r-1 earlier neighbors, and has a degree-at-most-three choice inside its own remaining part. Thus every finite graph in this cover is (r+2)-degenerate and is (r+3)-choosable. For r=1, ordinary three-colorability is better than this list-color bound.

In particular, a six-chromatic finite unit graph cannot be covered by two unit triangular lattices. Three lattices are only a necessary minimum for this method, not a sufficient construction.

## 5. Parallel translates have a stronger bound

**Theorem 5.** A union of m translates of a single oriented unit triangular lattice has chromatic number at most max(3,m).

**Proof.** Discard duplicate cosets, and write the distinct ones as t_i+Lambda. For two cosets there is at most one unit vector in t_j-t_i+Lambda. Otherwise the origin would be an external point with two unit neighbors in that coset, contrary to Lemma 1.

When such a vector exists, all cross edges between these cosets have the form

    t_i+z  ~  t_j+z+h_ij

for a fixed h_ij in Lambda. Let k=max(3,m) and define the additive lattice coloring

    ell(a+b omega) = a-b mod k.

The six unit directions have values plus/minus 1 or plus/minus 2, all nonzero for k>=3. Color the ith coset by ell(z)+s_i. A cross-edge family forbids just one value of s_j-s_i. Choose the offsets s_i successively. At the ith step there are at most i-1 forbidden choices and k>=m colors. This produces a proper coloring of the entire union. QED.

Thus at most five parallel triangular-lattice cosets cannot supply a six-chromatic graph. This is an ordinary chromatic bound, not a claimed k-choosability theorem for that value of k.

## 6. The six-corner pressure lemma

**Theorem 6.** Let Q be a finite subset of a unit triangular lattice, with an allowed-color list L(v) of size at least three at every vertex. If Q has no proper list-coloring, there is a vertex-minimal uncolorable induced subset T with the following properties:

1. T has at least six distinct convex-hull vertices.
2. Every convex-hull vertex v has degree exactly three in T and |L(v)|=3.
3. Every interior angle of conv(T) is at least 120 degrees.

**Proof.** Minimality implies deg_T(v)>=|L(v)|>=3: otherwise color T-v and extend to v. The set is not collinear. At a convex-hull vertex, the incident edges occupy an angle strictly less than 180 degrees. Among the six triangular-lattice unit directions, this permits at most three neighbors. Hence the degree and list size both equal three. Three distinct unit directions in an angle smaller than 180 degrees span at least 120 degrees. The exterior turn at every hull corner is therefore at most 60 degrees. The total exterior turn of a convex polygon is 360 degrees, so there are at least six corners. QED.

**Corollary.** If lists have size at least three everywhere and at most five vertices have lists of size exactly three, then the finite triangular-lattice graph is list-colorable.

### Interpretation for five-color geometric extension

After coloring an outside graph, a new vertex has the five-color palette minus the colors appearing at its colored unit neighbors. In the regime where each new vertex loses at most two distinct colors, an extension failure must have at least six spatially distinct hull vertices each losing exactly two colors. These must surround a residual region; a single heavily constrained point does not suffice.

If all the precolored neighbors in this argument lie outside the new lattice, Lemma 1 says one such outside point can constrain only one new lattice vertex. The six tight hull vertices therefore require at least twelve distinct outside neighbor points, representing two different forbidden colors at each corner.

**Scope warning.** The twelve-point conclusion assumes those colored points really lie outside the lattice. A precolored intersection point belonging to that lattice can constrain several new vertices, so it must not be counted as an external one-port neighbor. For three pairwise disjoint lattice layers, the per-vertex two-neighbor bound applies directly; for layers with common points, those points need separate treatment. The six-corner list theorem itself is independent of these geometric interpretations.

This is a necessary pressure condition, not a constructed uncolorable list assignment and not a six-color lower bound.

## 7. A finite-contact observation for concentric incommensurate lattices

Here complex notation is useful. Let K=Q(sqrt(-3)), Lambda=Z[omega], and let rho be a complex unit with rho not in K. Then Lambda and rho Lambda meet only at zero.

**Theorem 7.** There are only finitely many unit pairs a in Lambda, rho b in rho Lambda, with a and b both nonzero.

**Proof.** Put t=b conjugate(a) in K. The unit equation implies

    2 Re(rho t) = |a|^2+|b|^2-1 in Z.

The set U={t in K : Re(rho t) in Q} is a rational vector subspace of K of dimension at most one. If it had dimension two, evaluating the functional on a rational basis of K would force both Re(rho) and sqrt(3) Im(rho) to be rational, hence rho in K.

If U=0 there are no such pairs. Otherwise all nonzero t lie on one real line through the origin. The angle of rho t is therefore fixed modulo pi. Write gamma for the absolute cosine of that angle. It is strictly smaller than one: equality would make rho t real and rational, again forcing rho in K. Hence

    1 >= (1-gamma)(|a|^2+|b|^2).

Both lattice vectors have bounded norm, giving finitely many pairs. QED.

For a fixed finite family of concentric lattices whose pairwise rotation ratios are outside K, all cross-contact endpoints are consequently finite in number. Once a lattice-convex finite patch in each layer includes every such endpoint and the common origin, arbitrary proper k-colorings of that finite union extend to the full union for k>=4, by the convex-precoloring argument. There is no uniform radius independent of the angles. Commensurate rotations in K are excluded from this observation.

This explains why blindly enlarging the radius of a fixed concentric construction may eventually add no new coupling information. It does not rule out useful finite contact cores.

## 8. Exact finite experiments

### Eight two-layer controls

For each of eight different rotations/translations, a radius-three triangular patch and a transformed copy were combined. Every actual unit pair was restored. The point sets have 73 or 74 vertices. For each of the 31 oriented color partitions of a distinguished first-layer wheel, the constructive extension algorithm produced a complete five-coloring.

All 8*31=248 colorings are stored and independently checked. The cases include Moser rotation, half-Moser rotation, the de Grey linking rotation, a quarter turn, a parallel irrational shift, and translated rotated copies. These are controls for the general proof, not the proof of its universal quantifier.

### Sparse multilayer attempts

Five three-layer and two four-layer radius-three candidates, with 109-146 vertices, all had explicit four-colorings and empty 5-cores. A nine-layer concentric example had 325 vertices and 882 unit edges; it too had a four-coloring and empty 5-core.

An empty 5-core means that repeated deletion of degree-at-most-four vertices removes everything. It is an explicit five-colorability certificate, not merely a failed search.

### Densification by Minkowski sums

Let alpha have cosine sqrt(33)/6 and sine sqrt(3)/6. Form the 31-point set consisting of zero and the 30 directions omega^i alpha^j, i=0,...,5, j=-2,...,2. Its pairwise sumset has 451 vertices and 1920 actual unit edges, with a 421-vertex 5-core. It has a stored four-coloring.

The union with its rotation by cosine 7/8 and sine sqrt(15)/8 has 901 vertices, 3906 unit edges and an 841-vertex 5-core. An initial bounded backtracking search returned UNKNOWN for both four and five colors. A separately implemented TabuCol search found a five-coloring, and the installed Z3 C library then found a four-coloring. Both are independently checked. The original UNKNOWN results are preserved as search history and are not mathematical negative results.

This is a concrete reminder that a large 5-core is only a necessary filter for six-chromaticity, not close evidence of it.

## 9. Direct attempts using an actual five-chromatic seed

The 1581-point de Grey graph was rebuilt from its published coordinate construction. Its faithful closure has 7877 unit edges, agreeing with the preceding project audit. This time its coordinate data and complete positive five-coloring are actually included in the package.

Let A=(-2,0). Four larger pure-unit graphs were constructed from this seed G:

- G union its rotation about A with cosine 5/6 and sine sqrt(11)/6;
- G union its rotation about A with cosine sqrt(33)/6 and sine sqrt(3)/6;
- G union its rotation about A with cosine 7/8 and sine sqrt(15)/8;
- G union (G+(1,0)).

| Construction | Vertices | Actual unit edges | Vertices in 5-core | Result |
|---|---:|---:|---:|---|
| Seed | 1581 | 7877 | 1557 | Explicit 5-coloring |
| Moser-angle copy | 3107 | 15894 | 3063 | Explicit 5-coloring |
| Half-Moser-angle copy | 3151 | 15842 | 3103 | Explicit 5-coloring |
| Linking-angle copy | 3161 | 16566 | 3137 | Explicit 5-coloring |
| Unit translation | 3008 | 16695 | 3004 | Explicit 5-coloring |

The four enlarged graphs contain the published five-chromatic seed and have independently checked five-colorings, so they are exactly five-chromatic, using the published seed theorem for the lower bound. No such enlarged graph is a six-color witness.

The searches used one Boolean variable per vertex/color, exactly-one clauses, and all unit-edge disequalities. Fixing one actual unit triangle to colors 0,1,2 only breaks global color symmetry. Positive model verification is independent of the solver.

## 10. A joint-frame audit, not just a chromatic-number check

The 3161-point linking-angle union was checked at the standard wheel centered at zero in the first copy and its corresponding wheel in the second copy. The first rim word was fixed to 010123 with center color 4. The second rim word was allowed to be 010123 or 010231. For each, all 120 permutations of the five color roles were considered.

The actual induced graph on these two interfaces permits 96 relative permutations for each second word, hence 192 baseline cases in total. Every one of those 192 assignments extends to a proper five-coloring of the full 3161-point graph. All 192 full colorings are stored and checked, together with independent recomputation of the baseline set.

Thus this particular joint projection gains no additional restriction from the large interiors beyond the bare two-interface geometry. This does not cover every root pair, every one of the 31 partitions, or higher-interface projections.

For the unit-translated union, fixing the first state-2 word and allowing all six oriented state-2 words at the corresponding translated wheel gives four locally permissible full labeled assignments. All four extend to the full 3008-point graph.

## 11. The critical distinction for the statistical compiler

A finite graph, or even a union of two entire lattices, being five-colorable does NOT by itself prove that every finite full-color congruence-distribution problem on it is feasible.

The statistical compiler compares patterns under isometries that need not preserve the two-lattice host. A separating certificate on a colorable patch could lead to a noncolorable union of additional isometric copies, involving more lattices. The earlier three-color Moser benchmark already illustrates this distinction.

Consequently:

- direct six-chromatic searches confined to two triangular lattices are excluded by Theorem 3;
- a nontrivial single-wheel five-color filter in such a host is excluded by Theorem 4 and the convex-precoloring corollary;
- statistical congruence certificates on colorable two-layer patches are NOT excluded merely by those extension results;
- a claim that an entire ambient ring kills the statistical route requires a suitable congruence-consistent law or geometric coloring, not just an ordinary coloring.

The R4 escape inequality remains a valid necessary condition. It has not been made incompatible with all actual five-colorings of a new cross-lattice graph in this run.

## 12. Search decisions now justified

The next target should be an actual failure of a five-color extension relation, or a rational full-color congruence certificate, not an increase in point count or edge count alone.

A direct triangular-sheet approach must escape two-sheet coverage. A parallel-sheet approach must escape five-coset coverage. In the disjoint three-sheet extension regime, a candidate needs enough two-color external pressure arranged around at least six tight hull corners, and must address all colorings of the already colored part, not one convenient choice.

Large known five-chromatic modules are legitimate alternatives to a small number of triangular sheets, but the four tested copies demonstrate that simply pasting two such modules is not enough. The selected 192-state audit also shows why a promising joint boundary must actually be measured rather than inferred from the size of the interiors.

A bounded exploratory search for bad three-lists on a 19-point lattice patch did not resolve that subproblem. Its completed 40-round run found an extension for every proposed list assignment. Some longer searches timed out without a completed certificate. None is cited as a choosability theorem or a negative result.

## 13. Verification and trust boundary

The new package contains 23 geometries. The independent verifier checked 469 complete positive witnesses in total, including the 248 rooted two-layer extensions, the 192 linking-angle joint extensions, the four translated joint extensions, and the positive coloring controls. Unit closures are recomputed exactly, not accepted from stored edge lists.

The arithmetic fields are Q(sqrt(3),sqrt(5),sqrt(11)) and Q(sqrt(3),sqrt(5),sqrt(7),sqrt(11)). A field element is represented by rational coefficients of the squarefree-radical basis. For large graphs, common denominators make every distance test an integer identity in that basis.

The independent geometry checker uses the rational coefficient of the squared norm as an exact sieve. Its positive diagonal terms bound each coordinate difference. Bucketing by four such coefficient coordinates excludes only pairs that cannot have rational norm coefficient one; surviving pairs are checked in every radical coefficient. This is not a floating geometric tolerance.

The checker imports no generation, Z3, NumPy, SciPy, or local-search code. Its full default run uses only Python's standard library. A resumable mode records hashes, but the distributed verification command runs fresh by default. No Lean/Coq formalization is claimed.

## 14. External references and source separation

- A. D. N. J. de Grey, *The chromatic number of the plane is at least 5*, arXiv:1804.02385v3. Source of the rebuilt five-chromatic seed and its published lower bound.
- J. K. Haugland, *A Moser-spindle-free 5-chromatic unit distance graph on 2131 vertices in the plane*, arXiv:2608.04542v4. Current external calibration and an example of relation composition, not a source of the new extension lemmas.
- A. Ducz, *A note on geometric colorings of the Moser lattice*, arXiv:2606.12325v1. Background on distinguishing ambient geometric colorings from ordinary colorability; no claim that its stated ring theorem automatically covers every coordinate field used here.
- Uploaded prior R4 report and certificate package. Source of the prior conditional-state and escape-inequality results, reverified at the beginning of this run.

All extension lemmas, the six-corner argument, and the finite-contact observation are proved in this document. No external source is being credited with them, and no novelty claim is made. The new finite results are tied to the included coordinates and witnesses.
