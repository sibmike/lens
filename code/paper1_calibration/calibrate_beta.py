"""Best-available calibration for Paper 1's beta coefficients.

Paper 1 §6 reports beta_merit = 0.79 and beta_delivery = 0.297, calibrated on
N=35 startups with k=10 raters. Per-rater human ratings with separable
merit/delivery features do NOT exist in this repo — only an averaged
expert_score per startup. We therefore cannot reproduce that specific
regression here.

What this script DOES is the closest reproducible analog: regress expert_score
against the four AI-derived component scores (market potential, solution
viability, team capability, initial traction) from
code/data/startup_evaluations_avg_anon.csv. The resulting coefficients are
NOT the published beta_merit / beta_delivery values; they are AI-component
loadings. The v2 paper editor must either:
  (a) ask the author for the merit/delivery feature definitions used in §6, or
  (b) replace §6's calibration narrative with this AI-component regression.

Run from the repo root:
    /c/Users/mikea/anaconda3/python.exe code/paper1_calibration/calibrate_beta.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.linear_model import LinearRegression

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "code" / "data" / "startup_evaluations_avg_anon.csv"

FEATURE_COLS = [
    "avg_market_potential_score",
    "avg_solution_viability_score",
    "avg_team_capability_score",
    "avg_initial_traction_score",
]


def main() -> None:
    df = pd.read_csv(DATA)
    print(f"Loaded {DATA.relative_to(REPO)}: {df.shape[0]} startups")
    needed = FEATURE_COLS + ["expert_score"]
    df = df.dropna(subset=needed).copy()
    print(f"Rows after dropping NA on required cols: {len(df)}")

    # Map the 1-5 scale onto (0, 1) so logit is defined; small epsilon avoids 0/1.
    eps = 1e-3
    target_prob = (df["expert_score"].to_numpy() - 1.0) / 4.0
    target_prob = np.clip(target_prob, eps, 1.0 - eps)
    y = logit(target_prob)

    X = df[FEATURE_COLS].to_numpy()
    model = LinearRegression().fit(X, y)

    print("\nRegression: logit(normalized expert_score) ~ AI component scores")
    print(f"  intercept: {model.intercept_:.4f}")
    for name, coef in zip(FEATURE_COLS, model.coef_):
        print(f"  beta[{name:42s}] = {coef:+.4f}")
    print(f"  R^2 (in-sample): {model.score(X, y):.4f}")

    print(
        "\nPaper 1 §6 reports beta_merit = 0.79 and beta_delivery = 0.297 from a "
        "different feature set (per-rater merit/delivery) not present in this repo. "
        "The coefficients above are best-available AI-component loadings; the v2 "
        "paper editor should reconcile."
    )


if __name__ == "__main__":
    main()
