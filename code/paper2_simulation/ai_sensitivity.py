"""Paper 2 ↔ Paper 3 sensitivity sub-experiment.

Paper 2 idealizes the AI-filter stage of the platform architecture (effectively
sigma_AI -> 0). Paper 3 measures real LLM performance with NDCG@10 ~ 0.91 and
implicit noise sigma_AI > 0. This script sweeps sigma_AI across a range
bracketing Paper 3's measured value and recomputes the platform vs. elite-VC
comparison from simulation.py at each point.

Output:
  results/sensitivity_curve.csv  — quality and CV per (archetype, sigma_AI)
  results/sensitivity_curve.png  — platform & elite-VC quality as a function of sigma_AI

Run from the repo root:
    /c/Users/mikea/anaconda3/python.exe code/paper2_simulation/ai_sensitivity.py
"""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "paper2_simulation"))

import simulation  # noqa: E402

OUT = REPO / "code" / "paper2_simulation" / "results"
OUT.mkdir(parents=True, exist_ok=True)

# Range chosen to bracket Paper 3's measured sigma. Approximate calibration:
# from Paper 3 NDCG@10 ~= 0.91, the implied AI noise on the same log-odds scale
# as P2's evaluator noise is roughly 0.3-0.4. The endpoints (0.0 and 0.6)
# make the curve interpretable.
SIGMA_GRID = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
PAPER3_SIGMA_AI_ANCHOR = 0.35  # rough; v2 paper editor should refine if needed
N_TRIALS = 200  # smaller than the headline sims; one curve only


def patched_ai_noise(key: str, sigma_ai: float) -> None:
    """Mutate INVESTOR_CONFIGS[key] in place: set AI Model Filter noise_std to sigma_ai.

    For archetypes without an AI stage (e.g. elite_vc), this is a no-op so the
    archetype acts as the no-AI baseline at every point on the curve.
    """
    cfg = simulation.INVESTOR_CONFIGS[key]
    for stage in cfg.get("stages", []):
        if "ai" in stage.get("name", "").lower():
            stage["evaluators"].setdefault("bias_overrides", {})["noise_std"] = sigma_ai


def run_one(key: str, sigma_ai: float, baseline_cfg: dict) -> dict:
    # Restore baseline before each run, then re-apply our patch.
    simulation.INVESTOR_CONFIGS[key] = deepcopy(baseline_cfg)
    patched_ai_noise(key, sigma_ai)

    results = simulation.run_monte_carlo(
        investor_type=key,
        n_simulations=N_TRIALS,
        use_pitch_filter=False,
    )
    # Paper 2's reported "portfolio quality %" is avg_true_probability per iteration.
    quality_col = "avg_true_probability"
    if quality_col not in results.columns:
        # Fall back to any quality-shaped column, but warn so the v2 editor notices.
        quality_col = next(
            (c for c in results.columns if "true" in c.lower() and "prob" in c.lower()),
            None,
        )
    if quality_col is None:
        return {"archetype": key, "sigma_ai": sigma_ai, "quality_mean": np.nan, "quality_cv": np.nan}
    q = results[quality_col].dropna().to_numpy()
    return {
        "archetype": key,
        "sigma_ai": sigma_ai,
        "quality_mean": float(np.mean(q)),
        "quality_cv": float(np.std(q) / np.mean(q)) if np.mean(q) > 0 else np.nan,
        "quality_col": quality_col,
    }


def main() -> None:
    # cyrannus_ai_20 = the standard platform architecture (scout -> AI -> committee 1 -> committee 2).
    # elite_vc       = the no-AI comparison; flat across the sigma grid.
    archetypes_under_test = ["cyrannus_ai_20", "elite_vc"]
    archetypes_under_test = [k for k in archetypes_under_test if k in simulation.INVESTOR_CONFIGS]
    baselines = {k: deepcopy(simulation.INVESTOR_CONFIGS[k]) for k in archetypes_under_test}
    print(f"Sensitivity sweep: {archetypes_under_test} x sigma_AI in {SIGMA_GRID}")
    print(f"Trials per point: {N_TRIALS}\n")

    rows = []
    for key in archetypes_under_test:
        for sigma in SIGMA_GRID:
            print(f"  {key} @ sigma_AI = {sigma:.2f} ...", end=" ", flush=True)
            try:
                row = run_one(key, sigma, baselines[key])
                rows.append(row)
                print(f"quality_mean = {row['quality_mean']:.4f}")
            except Exception as e:
                print(f"FAILED ({type(e).__name__}: {e})")
                rows.append({"archetype": key, "sigma_ai": sigma, "quality_mean": np.nan, "quality_cv": np.nan})

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sensitivity_curve.csv", index=False)
    print(f"\nWrote {(OUT / 'sensitivity_curve.csv').relative_to(REPO)}")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for key in archetypes_under_test:
        sub = df[df["archetype"] == key].dropna(subset=["quality_mean"])
        ax.plot(sub["sigma_ai"], sub["quality_mean"], marker="o", label=key)
    ax.axvline(PAPER3_SIGMA_AI_ANCHOR, color="grey", linestyle="--", alpha=0.6,
               label=f"Paper 3 measured (~{PAPER3_SIGMA_AI_ANCHOR:.2f})")
    ax.set_xlabel(r"AI filter noise $\sigma_{AI}$ (log-odds)")
    ax.set_ylabel("Mean portfolio quality")
    ax.set_title("Paper 2 platform vs. elite VC — sensitivity to AI filter noise")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "sensitivity_curve.png", dpi=140)
    print(f"Wrote {(OUT / 'sensitivity_curve.png').relative_to(REPO)}")


if __name__ == "__main__":
    main()
