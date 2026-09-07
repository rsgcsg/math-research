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

`make check` uses only the Python standard library. It checks all saved positive
SAT models without importing the SAT solver or search encoder. It also compares
finite tables with exact re-enumeration and checks the hashes of archived inputs.
The symbolic arguments and infinite-family proofs are in `docs/proofs/`.

The three recorded UNSAT torus results are **uncertified search observations**;
the verifier deliberately does not turn them into negative mathematical claims.
No stored artifact is a certificate that the plane requires six or seven colors.
No Lean/Coq formalization is claimed.
