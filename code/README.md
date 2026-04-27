# LENS Trilogy — Code

Reproduction code for the three LENS papers in [`papers/`](../papers/). All scripts are self-contained and run against anonymized data in [`data/`](data/); no confidential source data is needed to reproduce the published numbers.

## Layout

```
code/
├── README.md                         (this file)
├── requirements.txt
├── data/                             anonymized inputs (no startup identities)
│   ├── ai_reviews_research_anon.csv          → Paper 3 NDCG aggregator
│   ├── ai_reviews_prod_anon.csv              → Paper 2 σ_AI anchor
│   ├── candidates_top_anon.csv               → broader candidate pool
│   ├── ratings_results_and_averages_anon.csv → near-duplicate of ai_reviews_research
│   ├── startup_evaluations_avg_anon.csv      → Paper 1 calibration
│   └── pitch_reviews_anon.csv                → single-AI-eval per startup
├── tools/
│   └── anonymize.py                  documents how data/ was generated from the
│                                     confidential sources held on the authors' machines
├── shared/
│   └── perception_model.py           the canonical logit(q̂) = logit(q) + βᵀx + ε
├── paper1_calibration/
│   └── calibrate_beta.py             best-available regression for Paper 1 §6
├── paper2_simulation/
│   ├── simulation.py                 PRISM Monte Carlo framework for Paper 2
│   ├── run_all_archetypes.py         orchestrator over the 11 archetypes
│   ├── ai_sensitivity.py             the Paper 2 ↔ Paper 3 sensitivity sweep (Paper 2 §5.6)
│   └── results/                      output dir for CSVs and PNGs
└── paper3_llm_eval/
    ├── pitch_evaluator.py            reference LLM evaluator implementation
    ├── prompts/                      the four prompting setups (s1–s4)
    ├── run_experiments.py            orchestrator for end-to-end re-runs (requires API keys)
    ├── aggregate_ndcg.py             reproduces Paper 3 Tables 1–3 from the anonymized data
    └── results/
```

## Paper-section crosswalk

| Paper | Section | Code | Anonymized data | Output |
|---|---|---|---|---|
| Paper 1 | §6 calibration | [paper1_calibration/calibrate_beta.py](paper1_calibration/calibrate_beta.py) | [data/startup_evaluations_avg_anon.csv](data/startup_evaluations_avg_anon.csv) | β coefficients printed |
| Paper 2 | §5.1 archetype hierarchy | [paper2_simulation/run_all_archetypes.py](paper2_simulation/run_all_archetypes.py) | (pure simulation) | results/results_*.csv |
| Paper 2 | §5.6 AI sensitivity | [paper2_simulation/ai_sensitivity.py](paper2_simulation/ai_sensitivity.py) | [data/ai_reviews_research_anon.csv](data/ai_reviews_research_anon.csv) | results/sensitivity_curve.{csv,png} |
| Paper 3 | §4 Tables 1–3 | [paper3_llm_eval/aggregate_ndcg.py](paper3_llm_eval/aggregate_ndcg.py) | [data/ai_reviews_research_anon.csv](data/ai_reviews_research_anon.csv) | results/table*_*.csv |

## How to run

```bash
pip install -r code/requirements.txt

# Paper 1 — best-available calibration
python code/paper1_calibration/calibrate_beta.py

# Paper 2 — the headline simulation (use --quick for a smoke test)
python code/paper2_simulation/run_all_archetypes.py --quick

# Paper 2 ↔ Paper 3 — sensitivity sweep
python code/paper2_simulation/ai_sensitivity.py

# Paper 3 — reproduce Tables 1–3 from the canonical results table
python code/paper3_llm_eval/aggregate_ndcg.py

# Paper 3 — verify prompt files load (no API calls)
python code/paper3_llm_eval/run_experiments.py --dry-run
```

## API credentials

Re-running the LLM evaluations end-to-end (`run_experiments.py` without `--dry-run`) requires:

- `ANTHROPIC_API_KEY` — Anthropic backend
- `OPENAI_API_KEY` — OpenAI backend

These are *not* needed to reproduce Paper 3's Tables 1–3, which are computed from the canonical per-startup score columns already present in [`data/ai_reviews_research_anon.csv`](data/ai_reviews_research_anon.csv). They are needed only to regenerate those scores from raw pitch transcripts.

Set the keys in your shell or in a local `.env` file (see [`.env.template`](../.env.template)). The `.env` file is gitignored.

## Confidentiality

[`data/`](data/) contains only anonymized derivatives. Each startup is identified by an opaque stable ID (`S001`…`SNNN`); founder names, contact information, video transcripts, and S3 URIs were stripped during anonymization. The original confidential CSVs are not part of this repository.

[`tools/anonymize.py`](tools/anonymize.py) documents the anonymization process for transparency. It cannot be run end-to-end without the confidential source data on the authors' machines, but the script is the authoritative description of which columns were dropped and how startup IDs were assigned.
