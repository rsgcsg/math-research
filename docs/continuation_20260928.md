# 2026-09-28 continuation: completed standalone publication

The remote base is `09926d59b176c1f649aa30f7ec397fb8fa9ef9fa`.
This continuation now includes the anchored finite-order palette normal form, the exact minimum-three law for S=F union Gamma union full eta, the three-atom weight classification, exact positive and negative certificates, independent standard-library checkers, and actual local/remote replay receipts.

The new code was tested on a clean checkout of the published base; it does not import the unpublished T141-T143 modules. The prior local checkpoint `f986eb0a0de1e33769efa54aa73c3eac9d2ff711` remains preserved in its existing supplied Git bundle, but its entire file tree and ancestry have not been merged by this standalone continuation. Descriptive result names avoid collisions with its historical numbering. The separately existing intrinsic-eta research branch was not changed.

The three complete Y partitions satisfy all 34 specified observations; only seven of the original fifteen full domains pass. Two exhaustive normalized two-state cases have independently replayed RUP refutations. The arbitrary-real-weight support minimum follows from the written majority-atom reduction. Three additional full-fifteen-domain searches are unverified restricted negatives, not mathematical conclusions. No original HN bound or arbitrary-support full-domain obstruction is claimed.

Start from [CURRENT](CURRENT.md) and [the complete proof](proofs/eta_joined_minimum_three.md). Replay with `make check-eta-support`. GitHub Actions run 36374324777 verified the actual published source commit 6ff96a8a7d489be7594adb68bb987b33b466eaff without solver packages; subsequent documentation does not alter the checked research source.
