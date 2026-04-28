# LENS — Layered Evaluation with Noise and Systematic-bias

> A founder pitches to ten venture firms. Three offer term sheets. The founder accepts the highest. Two years later the startup fails, and the winning firm runs a post-mortem: *why do we keep losing money on deals we win?*
>
> Across town, an HR executive runs a recruiting initiative explicitly designed for diversity. Blind résumé screens. Broadened outreach. Three years later the engineering team is 90% from the same demographic and the same three schools.
>
> A grant program officer notices the proposals winning their committee's review have a particular flavor — credentialed, conventional, prestigious. The committee was deliberately expanded from three members to twelve to fix exactly this. The bias didn't budge.

These look like three different problems. They are the same problem.

This repository is the working out — a math framework, a simulation, and a working LLM filter — of why multi-stage human selection systems produce the patterns they produce, and what you can do architecturally about it.

---

## The headline claims

- **One equation derives six selection phenomena.** $\mathrm{logit}(\hat q) = \mathrm{logit}(q) + \beta^\top x + \varepsilon$. From this single decomposition fall the winner's curse, contrarian advantage, the homogeneity trap, batch evaluation superiority, the committee paradox, and the disproportionate power of recommendations. Paper 1.
- **An angel with platform architecture beats elite VCs by 11.4% — under the model.** Across ~2,200 Monte Carlo simulation runs spanning eleven investor archetypes, a platform-enabled angel achieves 3.91% portfolio quality vs. 3.51% for an elite VC and 1.50% for a solo angel. The gain comes from the multi-stage architecture, not from a better evaluator. Paper 2.
- **An LLM ranks startup pitches at NDCG@20 = 0.92 against a ten-expert panel** *in-sample on N = 35* (permutation-test $p < 10^{-5}$, bootstrap 95% CI ≈ [0.85, 0.96]). The LLM is the first-stage filter; the human expert is the final stage. Paper 3.

The trilogy demonstrates internal coherence and operational feasibility. It does not yet establish out-of-sample investment performance or causal effects on realized startup outcomes — that's the next, outcome-anchored study.

---

## The papers

| | Paper | Posture |
|---|---|---|
| 1 | **[LENS: A Mathematical Foundation for Human Decision-Systems Engineering](papers/paper1_lens.md)** ([PDF](papers/pdf/paper1_lens.pdf)) | The framework. Log-odds perception model with calibration on N = 35 startups. |
| 2 | **[The Platform Paradox: When Angels with Architecture Outperform Elite VCs](papers/paper2_platform_paradox.md)** ([PDF](papers/pdf/paper2_platform_paradox.pdf)) | Monte Carlo stress test of the framework across eleven investor archetypes. |
| 3 | **[Instruction Distillation for Startup Pitch Ranking](papers/paper3_instruction_distillation.md)** ([PDF](papers/pdf/paper3_instruction_distillation.pdf)) | A working LLM filter built by reverse-engineering an expert panel's implicit rubric. |

If you only have time for one, **start with Paper 1** — the others are conditional on its model.

---

## What you get from reading

- A model of human evaluation that's bounded (lives in log-odds), separates systematic from random error, and survives committee aggregation under correlated bias.
- Three named theorems and a design proposition: order-statistic gap under batch ranking, committee aggregation under correlated bias, the winner's curse, and a heuristic for stage advancement rates under cost asymmetry.
- A simulation framework that lets you compose investor archetypes from primitives (batchers, evaluator pools, selectors) and measure portfolio quality, consistency, and scale.
- A reproducible LLM-evaluation pipeline that prompts a model with a methodology *distilled from the expert panel itself*, instead of trying to ask experts to articulate criteria they cannot articulate.

---

## Reproducing the numbers

```bash
pip install -r code/requirements.txt
cp .env.template .env          # API keys for Paper 3 LLM re-runs (optional)

# Paper 3 — NDCG ranking against a ten-expert panel
python code/paper3_llm_eval/aggregate_ndcg.py

# Paper 2 — Monte Carlo across eleven investor archetypes (--quick = smoke test)
python code/paper2_simulation/run_all_archetypes.py --quick

# Paper 2 ↔ Paper 3 — AI-filter sigma sensitivity sweep
python code/paper2_simulation/ai_sensitivity.py

# Paper 1 — best-available calibration from the public CSV
python code/paper1_calibration/calibrate_beta.py
```

The full paper-section-to-code crosswalk is in [`code/README.md`](code/README.md).

---

## Repository layout

```
papers/                           — three Markdown sources + built PDFs
  paper1_lens.md
  paper2_platform_paradox.md
  paper3_instruction_distillation.md
  pdf/                            — rebuilt via pandoc + xelatex
code/
  data/                           — anonymized inputs (no startup identities)
  paper1_calibration/             — Paper 1 regression on committee scores
  paper2_simulation/              — Paper 2 archetype simulation + sensitivity
  paper3_llm_eval/                — Paper 3 NDCG pipeline + prompts
  shared/                         — canonical perception model
```

---

## Data and scope

The original startup data — names, transcripts, contact info — is **confidential and not in this repository**. All released analyses use anonymized derivatives in [`code/data/`](code/data/), with each startup keyed to an opaque stable ID. The anonymized rankings are sufficient to reproduce the headline NDCG numbers in Paper 3 and the regression in Paper 1.

The empirical surface area is small (N ≈ 34–35 startups, ten experts each, two LLM providers). It's a proof-of-concept, not external validation. Larger-N replication, multi-domain calibration, and outcome-anchored estimation are the natural next study and are explicitly out of scope here.

---

## Citation

Pending arXiv submission. For now:

> Arbuzov, M. L., & Mosbacker, L. (2025). *LENS: Layered Evaluation with Noise and Systematic-bias.* Cyrannus Inc.

---

## License and contact

MIT — see [LICENSE](LICENSE). Open an issue for questions, or reach the authors through the channels listed in the papers.
