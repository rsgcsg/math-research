# Evidence

- `phase_checks.json`: fully reproducible exact finite tables and small
  calibrations. Regenerate with `python3 research/export_certificates.py`.
- `search_models.json`: bounded SAT runs plus full positive models. Reproduce
  with `.venv/bin/python research/replay_searches.py`.
- `seam_radius3.json`, `seam_radius4.json`: complete binary-family word-pair
  relation counts at the specified Moser-angle seam. Reproduce with
  `python3 research/seam_relations.py --radius 3 --output certificates/seam_radius3.json`
  and analogously radius 4. Verified independently using the proved contact classification.
- `translated_seam.json`: all 384 translated-triple inputs, counts and palette
  witnesses (T017). Reproduce with
  `python3 research/translated_seam.py --output certificates/translated_seam.json`.
- `layer_relations.json`: complete 32-case uniform-phase classification (T019),
  with 28 positive witnesses; the four negative cases use the T018 proof.
  Reproduce with
  `python3 research/layer_relations.py --output certificates/layer_relations.json`.
- `layer_extension.json`: 1536 maximal-constraint positive witnesses covering
  arbitrary double-infinite binary words (T020). Reproduce with
  `python3 research/layer_extension.py --output certificates/layer_extension.json`.
  The independent checker verifies the entire covering index set and every
  permutation and edge constraint; the normalization and completeness argument
  is in `docs/proofs/translated_seam.md`. This is a restricted-family theorem,
  not an activation theorem for arbitrary plane colorings.
- `long_chain_invariant.json`: 36 nonempty frame sets closed under all 416
  admissible transition obligations. Reproduce with
  `python3 research/long_chain.py --output certificates/long_chain_invariant.json`.
  `verify_long_chain.py` independently rebuilds relations in global coordinates;
  this is an all-length inductive certificate, not a bounded-length experiment.
- `snail_replay.json`: exact independent replay summary and source archive hash
  for the external G29 geometric fractional dual. Reproduce with
  `python3 research/snail_replay.py --output certificates/snail_replay.json`;
  the downloaded archive belongs in ignored `references/cache/`.
- `joint_face_experiment.json`: numerical LP experiment restricted to the
  supplied 168-atom support of G27. Neither support completeness nor numerical
  negative claims are certified by this historical experiment file; superseded
  for positive-law conclusions by the exact artifacts below.
- `g27_replay.json`: original G27 dual replay summary, source hashes and exact
  168 zero-slack masks. Reproduce with `python3 research/g27_replay.py --output
  certificates/g27_replay.json` using the three documented cached source files.
  Source replay is separate from the offline positive-law checks.
- `joint_face_exact.json`: exact full-partition invariant laws: a three-atom
  non-deterministic extreme law and a strictly positive law on all 348 candidate
  covers. `verify_joint_face.py` independently checks all congruences using
  integer geometry and three-anchor reconstruction, without the search code.
  The optional stored 72-column kernel is search-side algebra, not independently
  certified by `make check`; only the stated positive laws are checked there.
- `parts509_core.json`: exact eight-component integer coordinates, all 2442
  induced unit edges, the public 2259-edge subgraph, and a full five-coloring.
  Independently reconstructed by `verify_parts_core.py` without SAT/search code.
- `parts509_reduced.lrat.gz`, `parts509_drat_replay.json`: saved RUP-only clausal
  refutation and provenance. The standard-library `verify_rup_lrat.py` rebuilds
  the 9548-clause formula and checks all 92649 derived clauses, including the
  empty clause. This is a replayed negative proof, not a solver-status label.
  The original public 46MB DRAT stays in ignored cache; the compressed LRAT is
  retained so `make check` can independently establish the five-chromatic core.
- `parts509_pairs.json`: 253 full five-colorings covering every nonunit pair's
  equality request and every distinct pair's inequality request (T026).
- `parts509_ports.json.gz`: all 22327 proper five-color boundary patterns on
  the specified central double hexagon, with a complete extension for each.
- `parts509_triples.json.gz`: 1744 full five-colorings cover every proper
  precoloring of all 21849334 vertex triples. `verify_parts_triples.py` uses
  witness-index intersections to independently check 106793611 legal patterns.
- `parts509_parallelograms.json.gz`: 3807 full colorings cover all 10725867
  legal partitions of 794256 equal-midpoint quadruples, including collinear ones.
  Search groups diagonals; `verify_parts_parallelograms.py` independently groups
  opposite directed sides and checks all witness intersections (T027).
- `residue11_coloring.json`: independently generated 121-vertex five-color table
  for the F11 unit-quadrance graph. `verify_residue11.py` checks all 726 finite
  edges, basis products and four exact Parts pullbacks. The extension to the
  entire number field K uses the written valuation proof (T028), not finite tests.
- `parts509_escape_rotations.json`: complete five-colorings for four 1017-vertex
  induced core doubles. `verify_parts_escape.py` squares all 1032256 noncommon
  cross-pair displacements in 16-dimensional exact fields, independently of the
  search's radial pruning. These do not color the entire extended fields.
- `pair_orbits_five.json.gz`: newly rebuilt historical five-orbit census,
  all 59049 labelled matching graphs, geometric exclusion witnesses and 245925
  full coloring words (including 196740 nonuniform-list words). Generate with
  `python3 research/pair_orbit_census.py`; independently check with
  `python3 research/verify_pair_orbits.py`. The old ZIP was not recovered.
- `pair_orbits_six_uniform.json.gz`: all 460728 forest-normalized six-pair
  models, covering 14348907 raw sign assignments. Positives are explicit
  three-colorings; negatives are K2,3/K4, rational rhombus implications, or the
  T035 real-conjugation trace obstruction. Generate with
  `python3 research/six_pair_uniform.py`; check with
  `python3 research/verify_six_pair_uniform.py`. Common three-lists ONLY:
  this does not certify the historical arbitrary-list six-orbit claim.
- `layer_residue_probe.json`: four bounded UNKNOWN observations for a periodic
  F11 layer quotient; no negative claim. Probe with
  `.venv/bin/python research/layer_residue_probe.py`; not a proof certificate.

`make check` uses only the Python standard library. It checks all saved positive
SAT models without importing the SAT solver or search encoder. It also compares
finite tables with exact re-enumeration and checks the hashes of archived inputs.
The symbolic arguments and infinite-family proofs are in `docs/proofs/`.

The three recorded UNSAT torus results are **uncertified search observations**;
the verifier deliberately does not turn them into negative mathematical claims.
No stored artifact is a certificate that the plane requires six or seven colors.
No Lean/Coq formalization is claimed.
