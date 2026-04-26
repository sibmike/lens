"""Anonymize the confidential source CSVs into code/data/ for shareable analysis.

Source files in tables/ and pitch_review/ are confidential and stay untouched.
This script writes anonymized derivatives under code/data/, replacing every
startup identifier with a stable startup_id of the form S001..SNNN. The
name->id mapping is persisted under tables/_private/name_to_id_map.csv so
the user can re-link if needed; that map never enters code/.

Run from the repo root:
    /c/Users/mikea/anaconda3/python.exe code/tools/anonymize.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
TABLES = REPO / "tables"
PITCH_REVIEW = REPO / "pitch_review"
OUT_DATA = REPO / "code" / "data"
PRIVATE = TABLES / "_private"

OUT_DATA.mkdir(parents=True, exist_ok=True)
PRIVATE.mkdir(parents=True, exist_ok=True)

IDENTITY_DROP_COLS = {
    "founder_name",
    "email",
    "phone",
    "Email Sent",
    "Responses ",
    "Due Diligence",
    "Action",
    "s3_uri",
    "video_hash_id",
    "transcript_text",
    "tldr_summary",
    "scout_batch",
    "founder_report_content",
    "email_content",
}
IDENTITY_DROP_PREFIXES = (
    "s3_",
    "market_potential_reasoning",
    "market_potential_suggestions",
    "solution_viability_reasoning",
    "solution_viability_suggestions",
    "team_capability_reasoning",
    "team_capability_suggestions",
    "initial_traction_reasoning",
    "initial_traction_suggestions",
    "founder_report",
    "video_moderation_labels",
    "transcript_moderation",
)

NAME_COL_CANDIDATES = ("startup_name", "company_name")


def build_master_name_map() -> dict[str, str]:
    """Stable map: union the three primary tables, sort by canonical expert score, S001..."""
    pieces: list[pd.Series] = []
    research = pd.read_csv(TABLES / "Ai Review Initial Pitches - ai_reviews_research (1).csv")
    research["_score"] = research["expert_score"]
    pieces.append(research[["company_name", "_score"]].rename(columns={"company_name": "name"}))

    top30 = pd.read_csv(TABLES / "Ai Review Initial Pitches - List top 30.csv")
    top30["_score"] = pd.to_numeric(top30.get("exp score"), errors="coerce")
    pieces.append(top30[["startup_name", "_score"]].rename(columns={"startup_name": "name"}))

    prod = pd.read_csv(TABLES / "Ai Review Initial Pitches - ai_reviews_prod.csv")
    prod["_score"] = pd.to_numeric(prod.get("overall_score"), errors="coerce")
    pieces.append(prod[["startup_name", "_score"]].rename(columns={"startup_name": "name"}))

    pr = pd.read_csv(PITCH_REVIEW / "ratings_results_and_averages.csv")
    pr["_score"] = pr["expert_score"]
    pieces.append(pr[["company_name", "_score"]].rename(columns={"company_name": "name"}))

    combined = pd.concat(pieces, ignore_index=True).dropna(subset=["name"])
    # collapse to one row per name with max known score for stable sorting
    by_name = combined.groupby("name", as_index=False)["_score"].max()
    by_name = by_name.sort_values(by=["_score", "name"], ascending=[False, True], na_position="last")
    by_name = by_name.reset_index(drop=True)
    by_name["startup_id"] = [f"S{i+1:03d}" for i in range(len(by_name))]
    by_name.to_csv(PRIVATE / "name_to_id_map.csv", index=False)
    return dict(zip(by_name["name"], by_name["startup_id"]))


def drop_identity_cols(df: pd.DataFrame) -> pd.DataFrame:
    keep = []
    for c in df.columns:
        if c in IDENTITY_DROP_COLS:
            continue
        if any(c.startswith(p) for p in IDENTITY_DROP_PREFIXES):
            continue
        keep.append(c)
    return df[keep].copy()


def anonymize_names(df: pd.DataFrame, name_map: dict[str, str]) -> pd.DataFrame:
    for col in NAME_COL_CANDIDATES:
        if col in df.columns:
            df["startup_id"] = df[col].map(name_map)
            df = df.drop(columns=[col])
    cols = ["startup_id"] + [c for c in df.columns if c != "startup_id"]
    return df[cols]


def write(df: pd.DataFrame, name: str) -> None:
    out = OUT_DATA / name
    df.to_csv(out, index=False)
    print(f"  -> {out.relative_to(REPO)}  ({df.shape[0]} rows x {df.shape[1]} cols)")


def main() -> None:
    print("Building master name map...")
    name_map = build_master_name_map()
    print(f"  {len(name_map)} unique startup names")
    print(f"  map written to {(PRIVATE / 'name_to_id_map.csv').relative_to(REPO)}")
    print()

    print("Anonymizing tables/Ai Review Initial Pitches - ai_reviews_research (1).csv ...")
    df = pd.read_csv(TABLES / "Ai Review Initial Pitches - ai_reviews_research (1).csv")
    df = anonymize_names(drop_identity_cols(df), name_map)
    write(df, "ai_reviews_research_anon.csv")

    print("Anonymizing tables/Ai Review Initial Pitches - ai_reviews_prod.csv ...")
    df = pd.read_csv(TABLES / "Ai Review Initial Pitches - ai_reviews_prod.csv")
    df = anonymize_names(drop_identity_cols(df), name_map)
    write(df, "ai_reviews_prod_anon.csv")

    print("Anonymizing tables/Ai Review Initial Pitches - List top 30.csv ...")
    df = pd.read_csv(TABLES / "Ai Review Initial Pitches - List top 30.csv")
    df = anonymize_names(drop_identity_cols(df), name_map)
    write(df, "candidates_top_anon.csv")

    print("Anonymizing pitch_review/ratings_results_and_averages.csv ...")
    df = pd.read_csv(PITCH_REVIEW / "ratings_results_and_averages.csv")
    df = anonymize_names(drop_identity_cols(df), name_map)
    write(df, "ratings_results_and_averages_anon.csv")

    print("Anonymizing pitch_review/startup_evaluations_avg.csv ...")
    df = pd.read_csv(PITCH_REVIEW / "startup_evaluations_avg.csv")
    df = anonymize_names(drop_identity_cols(df), name_map)
    write(df, "startup_evaluations_avg_anon.csv")

    print("Anonymizing pitch_review/pitch_reviews.csv ...")
    df = pd.read_csv(PITCH_REVIEW / "pitch_reviews.csv")
    df = anonymize_names(drop_identity_cols(df), name_map)
    write(df, "pitch_reviews_anon.csv")

    print("\nDone. All outputs under code/data/ are safe to share.")


if __name__ == "__main__":
    main()
