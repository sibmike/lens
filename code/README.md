# LENS Trilogy — Code

Cleaned, paper-organized code for the LENS trilogy. Every file here either ports a canonical script from `pitch_review/` or `pitch_review_simulation/`, or implements a new piece needed to reproduce or extend the papers' results.

The companion document is [../lens_trilogy.md](../lens_trilogy.md), which states the conceptual through-line and per-paper claims.

## Layout

```
code/
├── README.md                         (this file)
├── requirements.txt
├── data/                             anonymized inputs (no startup identities)
│   ├── ai_reviews_research_anon.csv          → Paper 3 NDCG aggregator
│   ├── ai_reviews_prod_anon.csv              → Paper 2 sigma_AI anchor
│   ├── candidates_top_anon.csv               → broader candidate pool
│   ├── ratings_results_and_averages_anon.csv → near-duplicate of ai_reviews_research
│   ├── startup_evaluations_avg_anon.csv      → Paper 1 calibration
│   └── pitch_reviews_anon.csv                → single-AI-eval per startup
├── tools/
│   └── anonymize.py                  one-shot: build code/data/ from confidential sources
├── shared/
│   └── perception_model.py           the canonical logit(q̂) = logit(q) + βᵀx + ε
├── paper1_calibration/
│   └── calibrate_beta.py             best-available beta regression (see notes)
├── paper2_simulation/
│   ├── simulation.py                 verbatim copy of pitch_review_simulation/simulation.py
│   ├── run_all_archetypes.py         orchestrator (replaces angels.ipynb / vc.ipynb / etc.)
│   ├── ai_sensitivity.py             NEW — Paper 2 ↔ Paper 3 sensitivity sweep
│   └── results/                      output dir for CSVs and PNGs
└── paper3_llm_eval/
    ├── pitch_evaluator.py            verbatim copy of pitch_review/pitch_test_claude.py
    ├── prompts/
    │   ├── setup1_component.py
    │   ├── setup2_guided.py
    │   ├── setup3_cot.py             (data missing from canonical results table)
    │   └── setup4_minimal.py
    ├── run_experiments.py            orchestrator (replaces 6 simple_*_pitch_test_*.ipynb)
    ├── aggregate_ndcg.py             NEW — reproduces Paper 3 Tables 2–4 from anonymized data
    └── results/
```

## Paper-section crosswalk

| Paper | Section | Code | Anonymized data | Output |
|---|---|---|---|---|
| P1 | §6 calibration | [paper1_calibration/calibrate_beta.py](paper1_calibration/calibrate_beta.py) | [data/startup_evaluations_avg_anon.csv](data/startup_evaluations_avg_anon.csv) | β coefficients printed |
| P2 | §5 Table 5.1 | [paper2_simulation/run_all_archetypes.py](paper2_simulation/run_all_archetypes.py) | (pure simulation) | paper2_simulation/results/results_*.csv |
| P2 | §5.X (NEW) AI sensitivity | [paper2_simulation/ai_sensitivity.py](paper2_simulation/ai_sensitivity.py) | [data/ai_reviews_research_anon.csv](data/ai_reviews_research_anon.csv) | results/sensitivity_curve.{csv,png} |
| P3 | §5.1.2 Tables 2–4 | [paper3_llm_eval/aggregate_ndcg.py](paper3_llm_eval/aggregate_ndcg.py) | [data/ai_reviews_research_anon.csv](data/ai_reviews_research_anon.csv) | paper3_llm_eval/results/table*_*.csv |

## How to run

Use the conda Python at `/c/Users/mikea/anaconda3/python.exe` (Python 3.12.4 with the deps in `requirements.txt`).

From the repo root:

```bash
# (one-time) regenerate anonymized data — only if the source CSVs change
/c/Users/mikea/anaconda3/python.exe code/tools/anonymize.py

# Paper 1 — best-available calibration
/c/Users/mikea/anaconda3/python.exe code/paper1_calibration/calibrate_beta.py

# Paper 2 — the headline simulation (use --quick for a smoke test)
/c/Users/mikea/anaconda3/python.exe code/paper2_simulation/run_all_archetypes.py --quick

# Paper 2 ↔ Paper 3 — sensitivity sweep
/c/Users/mikea/anaconda3/python.exe code/paper2_simulation/ai_sensitivity.py

# Paper 3 — reproduce Tables 2–4
/c/Users/mikea/anaconda3/python.exe code/paper3_llm_eval/aggregate_ndcg.py

# Paper 3 — verify prompt files load (no API calls)
/c/Users/mikea/anaconda3/python.exe code/paper3_llm_eval/run_experiments.py --dry-run
```

## API credentials

LLM evaluations require:
- `ANTHROPIC_API_KEY` — Anthropic backend
- `OPENAI_API_KEY` — OpenAI backend

These are not needed to reproduce Tables 2–4 from the canonical results table; only to re-run experiments end-to-end.

## Confidentiality

`code/data/` contains only anonymized derivatives. Each startup is identified by an opaque stable ID (`S001`…`SNNN`). The original confidential CSVs in `tables/` and `pitch_review/` are read-only and never copied raw into `code/`. The name↔id map is stored privately in `tables/_private/name_to_id_map.csv`.

Anything inside `code/` is safe to share publicly.

## Known issues for the v2 paper editor

These are findings surfaced during cleanup that the executor session writing `paper{1,2,3}_v2.md` must address:

1. **Paper 1 calibration is not reproducible from this repo.** No per-rater human ratings exist; only averaged `expert_score` per startup. The published β_merit = 0.79 / β_delivery = 0.297 used a feature decomposition (substantive vs. presentational) not present in any CSV. `calibrate_beta.py` runs the closest analog (regression of `expert_score` on AI-component features) and prints β coefficients of a different sort.
2. **Paper 3 setup s3 (chain-of-thought) is missing from the canonical results table.** `ai_reviews_research_anon.csv` has only s1, s2, s4 columns. Paper 3 §3 lists 4 setups; either re-run s3 or correct the prose.
3. **Paper 3 NDCG encoding.** The published Table 4 numbers (0.924, 0.923, 0.977) match `aggregate_ndcg.py` under **exponential gain** (`2^rel - 1`), not linear gain. Linear gain produces uniformly higher NDCG. The encoding choice is implicit in the paper and should be stated explicitly.
4. **Paper 3 N inconsistency.** Paper claims N = 40; canonical results table has 35 rows.
5. **Paper 2 ↔ Paper 3 reconciliation.** `ai_sensitivity.py` plots how the platform-vs-elite-VC ranking depends on σ_AI; the v2 paper editor should drop the resulting figure into a new short subsection in Paper 2 §5.

## Stale code

The original `pitch_review/` and `pitch_review_simulation/` folders are kept untouched but are superseded for paper purposes — see `STALE.md` in each. The `guidelines/` folder at the repo root is leftover Tycheism material and is unrelated to LENS.
