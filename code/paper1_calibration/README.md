# Paper 1 — Calibration

Paper 1 §6 reports `β_merit = 0.79`, `β_delivery = 0.297`, calibrated on N = 35 startups with ≈ 10 raters per startup. Per-rater human ratings — and specifically, separable merit/delivery features — **do not exist in this repo**. Only averaged `expert_score` per startup is available (in [../data/startup_evaluations_avg_anon.csv](../data/startup_evaluations_avg_anon.csv) and the wider research table).

## What `calibrate_beta.py` does

The closest reproducible analog: regress `logit((expert_score − 1)/4)` on the four AI-derived component scores (market potential, solution viability, team capability, initial traction) for the same N = 35 startups. This produces β coefficients of a different sort — AI-component loadings — and is *not* directly comparable to the published β_merit / β_delivery.

## Action for the v2 paper editor

Either:

(a) **Ask the author for the merit/delivery feature definitions** used in §6. If those features are derivable from any data still on the author's machine, re-run the regression there and either keep or update the published β values.

(b) **Replace §6's calibration narrative** with the AI-component regression `calibrate_beta.py` produces, and reframe §6 as showing that the LENS perception model fits the data with R² ≈ 0.75 even with AI-derived features standing in for human merit/delivery judgments.

Option (a) is preferred if the author has the merit/delivery features; option (b) is acceptable if not.
