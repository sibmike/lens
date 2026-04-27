# LENS — Layered Evaluation with Noise and Systematic-bias

A research trilogy formalizing how multi-stage human selection systems work and how to engineer them. The papers move from theory → simulation → real system, applied to venture-capital startup evaluation but generalizing to any high-stakes selection process.

## The papers

- **Paper 1 — LENS: A Mathematical Foundation for Human Decision-Systems Engineering.** Introduces the perception model `logit(q̂) = logit(q) + βᵀx + ε` and shows it explains six selection phenomena (winner's curse, contrarian advantage, homogeneity trap, batch superiority, committee paradox, recommendation power). Theory.
- **Paper 2 — The Platform Paradox: When Angels with Architecture Outperform Elite VCs.** Validates LENS via 2,200 Monte Carlo configurations across eleven investor archetypes. Headline: a platform-enabled angel achieves 3.91% portfolio quality, beating elite VCs (3.51%) and outperforming solo angels (1.50%) by 160%. Architecture beats individual ability. Simulation.
- **Paper 3 — Instruction Distillation for Startup Pitch Ranking.** Operationalizes the AI filter in Paper 2 with real LLMs (Claude, GPT-4) ranking 35 startups; achieves NDCG@20 = 0.923 against expert consensus. Empirical.

## Repository layout

```
.
├── README.md                              ← you are here
├── papers/
│   ├── paper1_lens.md                     ← Paper 1: framework
│   ├── paper2_platform_paradox.md         ← Paper 2: simulation
│   └── paper3_instruction_distillation.md ← Paper 3: empirical
└── code/
    ├── README.md                          ← code-tree map and run instructions
    ├── requirements.txt
    ├── data/                              ← anonymized inputs (no startup identities)
    ├── shared/                            ← canonical perception model
    ├── tools/
    │   └── anonymize.py                   ← documents the anonymization process
    ├── paper1_calibration/
    ├── paper2_simulation/
    └── paper3_llm_eval/
```

## Quick start

```bash
pip install -r code/requirements.txt
cp .env.template .env          # fill in API keys for LLM re-runs (optional)

# Reproduce Paper 3 NDCG tables
python code/paper3_llm_eval/aggregate_ndcg.py

# Run Paper 2 simulation (use --quick for a smoke test)
python code/paper2_simulation/run_all_archetypes.py --quick

# Paper 2 ↔ Paper 3 sensitivity sweep
python code/paper2_simulation/ai_sensitivity.py

# Paper 1 best-available calibration
python code/paper1_calibration/calibrate_beta.py
```

See [`code/README.md`](code/README.md) for the full paper-section ↔ code crosswalk.

## Data availability

The underlying startup data — names, transcripts, contact information — is **confidential and not included in this repository**. All analyses use anonymized derivatives in [`code/data/`](code/data/), where each startup is identified by an opaque stable ID (`S001`, `S002`, …). Anonymized rankings are sufficient to reproduce the NDCG and regression results reported in Papers 1 and 3.

The original confidential CSVs live only on the authors' machines in directories that are excluded by `.gitignore` (`tables/`, `pitch_review/`, `pitch_review_simulation/`).

## Sample size and scope

The empirical results draw on N ≈ 34 startups, sufficient as a proof-of-concept but insufficient for strong external validity. Larger-N replication is the natural follow-up and is out of scope for this trilogy.

## Citation

If you use any part of LENS in your own work, please cite the trilogy collectively pending arXiv submission:

> Arbuzov, M., et al. *LENS: Layered Evaluation with Noise and Systematic-bias.* 2025.

## License

MIT — see [`LICENSE`](LICENSE).

## Contact

Open an issue on this repository, or reach the author through the channels listed in the papers.
