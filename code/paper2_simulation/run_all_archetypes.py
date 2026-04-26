"""Orchestrator: run the 11 investor archetypes from simulation.py.

Replaces the per-archetype notebooks (angels.ipynb, vc.ipynb, vectorized.ipynb,
pitch_review_simulation_full.ipynb) that were used to generate Paper 2's
results CSVs. Produces one results CSV per archetype under results/.

Run from the repo root:
    /c/Users/mikea/anaconda3/python.exe code/paper2_simulation/run_all_archetypes.py            # full
    /c/Users/mikea/anaconda3/python.exe code/paper2_simulation/run_all_archetypes.py --quick    # smoke test
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "paper2_simulation"))

import simulation  # noqa: E402  (path-dependent)

OUT = REPO / "code" / "paper2_simulation" / "results"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a smoke test with 50 monte-carlo trials per archetype "
        "(default: paper-published trial count from INVESTOR_CONFIGS).",
    )
    parser.add_argument(
        "--archetypes",
        nargs="*",
        help="Subset of archetype keys to run; omit for all.",
    )
    args = parser.parse_args()

    archetypes = args.archetypes or list(simulation.INVESTOR_CONFIGS.keys())
    n_simulations = 50 if args.quick else 1000
    print(f"Running {len(archetypes)} archetypes x {n_simulations} simulations each.")

    for key in archetypes:
        cfg = simulation.INVESTOR_CONFIGS.get(key)
        if cfg is None:
            print(f"  skip {key}: not in INVESTOR_CONFIGS")
            continue
        print(f"  -> {key} ({cfg['name']}) ...")
        try:
            for use_pitch_filter, suffix in [(False, "baseline"), (True, "filtered")]:
                results = simulation.run_monte_carlo(
                    investor_type=key,
                    n_simulations=n_simulations,
                    use_pitch_filter=use_pitch_filter,
                )
                out_path = OUT / f"results_{key}_{suffix}.csv"
                results.to_csv(out_path, index=False)
                print(f"     wrote {out_path.relative_to(REPO)} ({len(results)} rows)")
        except Exception as e:
            print(f"     FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
