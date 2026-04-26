"""Reproduce Paper 3 NDCG tables from the canonical anonymized results.

Consumes code/data/ai_reviews_research_anon.csv (35 rows × 25 cols, including
expert_score as ground truth and the per-setup AI scores
s1_anthropic_1, s1_anthropic_2, s1_openai_1, s1_openai_2, ..., s4_openai_2).

Produces three tables matching Paper 3 §5.1.2:
  Table 2 — NDCG per (setup, model, run)
  Table 3 — NDCG per (setup, model) averaged across runs
  Table 4 — NDCG per averaging strategy (avg, avg_meth, avg_no_meth)

Run from the repo root:
    /c/Users/mikea/anaconda3/python.exe code/paper3_llm_eval/aggregate_ndcg.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "code" / "data" / "ai_reviews_research_anon.csv"
OUT = REPO / "code" / "paper3_llm_eval" / "results"
OUT.mkdir(parents=True, exist_ok=True)

SETUPS = ["s1", "s2", "s3", "s4"]
MODELS = ["anthropic", "openai"]
RUNS = [1, 2]
KS = [10, 20, 35]


def dcg(relevances: np.ndarray) -> float:
    """Standard DCG with log2(i+2) discount; relevances must be in predicted-rank order."""
    n = len(relevances)
    if n == 0:
        return 0.0
    discounts = 1.0 / np.log2(np.arange(2, n + 2))
    return float(np.sum(relevances * discounts))


def ndcg_at_k(
    predicted_scores: np.ndarray,
    true_scores: np.ndarray,
    k: int,
    encoding: str = "exp",
) -> float:
    """NDCG@k for a single ranking.

    `encoding` selects the gain function applied to true_scores:
      - "linear"  : gain_i = true_scores[i]                    (paper's most-likely choice; wide spread)
      - "exp"     : gain_i = 2**true_scores[i] - 1             (classical NDCG)
      - "binary"  : gain_i = 1 if rank_in_top_k_by_truth else 0 (top-k-cutoff version)
    """
    k = min(k, len(true_scores))
    pred_order = np.argsort(-predicted_scores, kind="stable")

    if encoding == "linear":
        pred_relev = true_scores[pred_order[:k]]
        ideal_relev = np.sort(true_scores)[::-1][:k]
    elif encoding == "exp":
        gains = np.power(2.0, true_scores) - 1.0
        pred_relev = gains[pred_order[:k]]
        ideal_relev = np.sort(gains)[::-1][:k]
    elif encoding == "binary":
        truth_order = np.argsort(-true_scores, kind="stable")
        top_k_truth = set(truth_order[:k].tolist())
        binary = np.array([1.0 if i in top_k_truth else 0.0 for i in range(len(true_scores))])
        pred_relev = binary[pred_order[:k]]
        ideal_relev = np.sort(binary)[::-1][:k]
    else:
        raise ValueError(f"unknown encoding: {encoding}")

    idcg = dcg(ideal_relev)
    if idcg == 0:
        return 0.0
    return dcg(pred_relev) / idcg


def table2_per_run(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (setup, model, run) with NDCG@{10,20,35}."""
    truth = df["expert_score"].to_numpy()
    rows = []
    for setup in SETUPS:
        for model in MODELS:
            for run in RUNS:
                col = f"{setup}_{model}_{run}"
                if col not in df.columns:
                    continue
                pred = df[col].to_numpy()
                rows.append(
                    {
                        "setup": setup,
                        "model": model,
                        "run": run,
                        "ndcg@10": ndcg_at_k(pred, truth, 10),
                        "ndcg@20": ndcg_at_k(pred, truth, 20),
                        "ndcg@35": ndcg_at_k(pred, truth, 35),
                    }
                )
    return pd.DataFrame(rows)


def table3_run_averaged(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (setup, model) with NDCG of the per-startup averaged scores."""
    truth = df["expert_score"].to_numpy()
    rows = []
    for setup in SETUPS:
        for model in MODELS:
            cols = [f"{setup}_{model}_{r}" for r in RUNS if f"{setup}_{model}_{r}" in df.columns]
            if not cols:
                continue
            pred = df[cols].mean(axis=1).to_numpy()
            rows.append(
                {
                    "setup": setup,
                    "model": model,
                    "ndcg@10": ndcg_at_k(pred, truth, 10),
                    "ndcg@20": ndcg_at_k(pred, truth, 20),
                    "ndcg@35": ndcg_at_k(pred, truth, 35),
                }
            )
    return pd.DataFrame(rows)


def table4_strategies(df: pd.DataFrame, encoding: str = "linear") -> pd.DataFrame:
    """The three pre-computed averaging strategies stored as columns in the source."""
    truth = df["expert_score"].to_numpy()
    strategies = {
        "avg (all setups)": "avg",
        "avg_meth (methodology setups)": "avg_meth",
        "avg_no_meth (no methodology setups)": "avg_no_meth",
    }
    rows = []
    for label, col in strategies.items():
        if col not in df.columns:
            continue
        pred = df[col].to_numpy()
        rows.append(
            {
                "strategy": label,
                "ndcg@10": ndcg_at_k(pred, truth, 10, encoding),
                "ndcg@20": ndcg_at_k(pred, truth, 20, encoding),
                "ndcg@35": ndcg_at_k(pred, truth, 35, encoding),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_csv(DATA)
    n_startups, n_cols = df.shape
    available_setups = [s for s in SETUPS if any(c.startswith(f"{s}_") for c in df.columns)]
    print(f"Loaded {DATA.relative_to(REPO)}: {n_startups} startups, {n_cols} cols")
    print(f"Setups present in data: {available_setups}  (missing: {set(SETUPS) - set(available_setups)})")
    print()

    if "s3" not in available_setups:
        print(
            "WARNING: setup s3 (chain-of-thought) is absent from the canonical results table.\n"
            "         Paper 3 §3 lists 4 setups; only 3 are present here.\n"
            "         The v2 paper must either re-run s3 or correct the prose to 3 setups.\n"
        )

    t2 = table2_per_run(df)
    t3 = table3_run_averaged(df)
    print("Table 2 — NDCG per (setup, model, run) [linear gain]:")
    print(t2.to_string(index=False))
    print("\nTable 3 — NDCG averaged over runs [linear gain]:")
    print(t3.to_string(index=False))
    print("\nTable 4 — NDCG by averaging strategy, under three relevance encodings.")
    print("Paper 3 reports avg @10/@20/@35 = 0.923787 / 0.922836 / 0.976521.\n")
    for encoding in ("linear", "exp", "binary"):
        t4 = table4_strategies(df, encoding=encoding)
        t4.to_csv(OUT / f"table4_strategies_{encoding}.csv", index=False)
        print(f"  encoding = {encoding}:")
        print(t4.to_string(index=False))
        print()

    t2.to_csv(OUT / "table2_per_run.csv", index=False)
    t3.to_csv(OUT / "table3_run_averaged.csv", index=False)
    print(f"Written to {OUT.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
