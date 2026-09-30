# T158(a): Exact nine-point P/R relaxation

## Result and scope

Let

`V = [4641, 877, 887, 3483, 5535, 7479, 7489, 229, 305]`.

Consider probability laws on all unlabeled partitions of V into at most five blocks that are proper on every actual unit edge induced by Y. For P and R, use exactly the pairs in the certified P/R transport components with both endpoints in V, and require every selected P event to have one common mean p and every selected R event one common mean r. All other pair events are unconstrained unless they are selected by these component intersections.

The exact projection onto (p,r) is the pentagon

- `12p + 3r >= 2`
- `r >= 0`
- `p <= 1/3`
- `2p + r <= 1`
- `2r - p <= 1`

with vertices, in cyclic order,

`(1/27,14/27), (1/6,0), (1/3,0), (1/3,1/3), (1/5,3/5)`.

Thus the sharp local minimum is `p=1/27`. At that minimum r is forced to the single value `14/27`. This is a result only for the specified nine-point local relaxation; its positive laws are not laws on all of Y and need not extend. It gives a necessary bound for a full-Y law, not a full15 obstruction or a plane chromatic-number result.

## Exact finite input

The checker reads `Y_full_geometry.json.gz`, `g14_pair_orbit_basis.json.gz`, `g14_r_pair_orbit_basis.json.gz`, and the T157 certificate from this repository. It binds the exact geometry to semantic SHA256 `90674956a11ac0b6627fb12c6bc108f1c4ddf2ca037c39a9271cf6ba896c0957`, the P forest to SHA256 `757a6f62edfb5285b9fde82f55c93454abd6e6a5b1985f3838d4c2a93e003534`, and the R component input to SHA256 `f21599cb3ed6076e797f1fed319d5e8d4941c50b05fdaed12c6de218a6e9c976`.

The induced unit graph on V has exactly eight edges:

`(229,887), (229,3483), (877,5535), (877,7479), (887,3483), (887,7489), (3483,7489), (5535,7479)`.

There are 14 P-component events on V and 5 R-component events. Their exact lists and provenance hashes are in `certificates/nine_point_pr_polygon.json`. In particular, `(229,877)` is in the P component and is included: it is an explicit P-forest node/edge, in addition to having squared distance 1/3. Pair selection is by membership in the certified component node sets, not by distance class. The verifier separately recomputes exact field distances for all 36 pairs and confirms the eight listed unit edges.

Restricted-growth enumeration generates all 18,002 partitions of V with at most five blocks; exactly 2,277 are proper on all eight actual unit edges (54 with 3 blocks, 714 with 4, and 1,509 with 5). The 14 P rows plus 5 R rows give 885 distinct event signatures among those partitions.

## Necessary inequalities: all-partition dual certificates

Let `e(a,b)` be 1 when a and b are in the same block, and 0 otherwise. Set

- `U = {4641,877,887,3483,5535,7479,7489}`
- `N7 = sum e(a,b)` over the 12 selected P pairs and 3 selected R pairs contained in U
- `T = e(229,4641) + e(305,4641) - e(229,305)`.

Every locally proper partition satisfies `N7 >= 2`: seven points in at most five blocks force at least two same-block pairs, and the six actual unit pairs within U cannot be same-block. Every partition also satisfies `T <= 1` by transitivity of being in the same block. Hence the integer-valued dual potential

`1 - 2*N7 + 3*T <= 0`

holds on every locally proper partition. Under the component-equality rows, `E[N7]=12p+3r` and `E[T]=2r-p`, so this dual gives `1-27p <= 0`, or `p>=1/27`. The exact checker evaluates the dual potential over all 2,277 partitions; its scores range from -12 to 0.

The remaining facets also have direct pointwise certificates:

1. `12p+3r>=2` follows from `N7>=2`.
2. `p<=1/3`: `{877,5535,7479}` is a unit triangle and each P pair from 4641 to that triangle is a selected component event. At most one of those three spokes can be same-block.
3. `2p+r<=1`: `{229,887,3483}` is a unit triangle; the selected spokes from 4641 have P type to 887 and 3483 and R type to 229. At most one spoke can be same-block.
4. `2r-p<=1`: for `{229,4641,305}`, the two sides from 4641 are R events and the base is a P event. The pointwise inequality `e(229,4641)+e(305,4641)-e(229,305)<=1` is a transitivity constraint.
5. `r>=0` is nonnegativity of an event expectation.

The verifier checks these pointwise conditions on each of the 2,277 local proper partitions, then intersects their rational halfplanes exactly. Their intersection is precisely the five-vertex polygon above.

At the minimum-p vertex, `12p+3r=2` and `2r-p=1` are both tight. Every atom in its 12-partition rational witness also has `N7=2` and `T=1`. This explains the sharpness: the local law simultaneously saturates the seven-point pigeonhole count and the three-point transitivity inequality.

## Exact positive witnesses

`certificates/nine_point_pr_polygon.json` gives a rational nonnegative weight and canonical restricted-growth partition for each atom at all five vertices. The standard-library checker verifies that each atom is proper, each law sums to one, and every one of the 14 P event means and 5 R event means equals the vertex's p or r exactly. Since the projected set is convex, feasibility at the five vertices proves feasibility throughout the pentagon.

## Replay

Run from the repository root:

`python -S research/verify_nine_point_pr_polygon.py`

The replay uses only Python's standard library and the repository's existing exact doubled-algebra arithmetic. It recomputes all 36 local squared distances, pins the geometry/component input hashes, and checks every individual event mean. Default execution compares the saved receipt; only explicit `--write-receipt` updates it. Optimized Python mode fails closed. No floating LP output is part of the certificate.

Part(b), [the complete P/R matching-window ceiling](pr_matching_window_ceiling.md), shows why adding that entire independently realizable local family cannot shrink this pentagon. Neither result supplies a jointly compatible full-Y law.
