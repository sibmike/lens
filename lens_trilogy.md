# LENS Trilogy — Logic and Map

Internal working reference for the three-paper LENS trilogy. Sections tagged `<!-- PUBLIC -->` are written so they can be lifted directly into a future public README; everything untagged is for the authors and Claude sessions cleaning up the papers and code.

## 1. Trilogy abstract <!-- PUBLIC -->

The LENS trilogy formalizes how multi-stage human selection systems work and how to engineer them. **Paper 1 (LENS)** introduces a single perception model — `logit(q̂) = logit(q) + βᵀx + ε` — and shows it explains six unrelated-looking phenomena in selection systems (winner's curse, contrarian advantage, homogeneity trap, batch superiority, committee paradox, recommendation power). **Paper 2 (Platform Paradox)** validates LENS with 2,200 Monte Carlo configurations across eleven investor archetypes and finds that *architecture beats individual ability*: an angel investor accessing a well-designed platform beats elite VCs (3.91% vs 3.51% portfolio quality, 160% above solo). **Paper 3 (Instruction Distillation)** instantiates the AI-filter stage that Paper 2 idealizes: real LLMs (Claude, GPT-4) ranking 35 anonymized startups achieve NDCG@20 = 0.923 against expert consensus, demonstrating that LLMs can serve as a defensible first-pass filter when prompted via instruction distillation. The three papers move from theory → simulation → real system; together they argue that selection performance is engineerable.

## 2. Through-line <!-- PUBLIC -->

```
        Paper 1 — LENS                Paper 2 — Platform Paradox        Paper 3 — Instruction Distillation
        (theory)                      (simulation)                      (empirical)
        ─────────────────             ─────────────────────             ──────────────────────────
        Define perception     ───►    Use it to simulate VC     ───►    Replace the idealized
        model & six           ───►    architectures; show              "AI filter" with real LLMs;
        phenomena.                    architecture > ability.          measure how good they are.

PRODUCES: q, q̂, β, ε,         PRODUCES: 11-archetype             PRODUCES: NDCG@10 = 0.908
          batch theorems,              comparison;                          (best single config),
          committee algebra,           CV as 3rd dimension;                NDCG@20 = 0.923
          stage sequencing.            sensitivity to AI σ.                (ensemble);
                                                                          instruction-distillation
                                                                          recipe.
CONSUMES: external claims     CONSUMES: P1 model & theorems.    CONSUMES: P1 model implicitly;
          (winner's curse                                                 P2's "AI stage" is what
          literature, etc.)                                               this paper instantiates.
```

The unidirectional dependency is **P1 → P2 → P3** in claim-strength: P1 is theoretical and load-bearing for the others; P2 borrows P1's model and tests architectural consequences; P3 borrows P2's framing of "AI filter as Stage 0" and shows it works in practice. The reverse-direction feedback that *should* exist — P3's measured AI noise feeding back into P2's simulation — is the missing seam this cleanup pass addresses with a sensitivity sub-experiment in P2.

## 3. Per-paper one-pager

### 3.1 Paper 1 — LENS: A Mathematical Foundation for Human Decision-Systems Engineering

**Claim.** <!-- PUBLIC --> A single decomposition `logit(q̂) = logit(q) + βᵀx + ε` (perceived = true + systematic-bias-on-features + noise) explains six selection phenomena that practitioners recognize but cannot derive: winner's curse, contrarian advantage, homogeneity compounding (e^(β·n_stages)), batch evaluation superiority via order statistics, committee size reducing noise by √k while leaving correlated bias unchanged, and recommendation power as a cost-free first-stage filter.

**Formal objects.** <!-- PUBLIC --> q (true quality), q̂ (perceived), β (bias vector), ε (random noise), x (observable features), k (committee size), n (pool size), s (selected), ρ_β (cross-evaluator bias correlation), ρ_ε (cross-evaluator noise correlation). Three load-bearing results: winner's curse `E[ε_winner] ≈ σ_ε √(log N)`; committee variance `Var(β̄) = σ²_β [ρ_β + (1−ρ_β)/k]`; batch advantage `σ_ε · Φ⁻¹((n−k+1)/n)` in log-odds.

**Evidence.** <!-- PUBLIC --> Calibration on N=35 startups with averaged expert scores. Reported coefficients: β_merit = 0.79, β_delivery = 0.297. The other phenomena are demonstrated analytically; their empirical validation is explicitly deferred to Paper 2 (P1 line 11: "Comprehensive validation appears in companion papers").

**Code artifacts.**
- Source: [pitch_review/ratings_results_and_averages.csv](pitch_review/ratings_results_and_averages.csv) (35×29; structurally identical to [tables/Ai Review Initial Pitches - ai_reviews_research (1).csv](tables/Ai Review Initial Pitches - ai_reviews_research (1).csv)).
- Cleaned: [code/data/ratings_results_and_averages_anon.csv](code/data/ratings_results_and_averages_anon.csv).
- Calibration script: [code/paper1_calibration/calibrate_beta.py](code/paper1_calibration/calibrate_beta.py) — best-available regression of `expert_score` on AI-derived component features (market, solution, team, traction). **This is not the same regression that produced the published β values**, because per-rater human merit/delivery ratings do not exist in the repo; see §7.

**Open issues.** Fourteen `NOTE:` editorial markers in the source (lines 7, 11, 53, 61, 65, 69, 73, 77, 81, 85, 89, 97, 105, 115). Missing citations: contrarian-returns claim (line 77), winner's curse origin, homophily compounding. Section 0 ("Notation and Assumptions") has a self-NOTE asking whether to move it to an appendix. Appendix references (A, B, C) appear in the body but no appendix content is present in the file.

### 3.2 Paper 2 — The Platform Paradox: When Angels with Architecture Outperform Elite VCs

**Claim.** <!-- PUBLIC --> Architectural design dominates evaluator skill. Across 2,200 Monte Carlo configurations spanning eleven investor archetypes, a platform-enabled angel achieves 3.91% portfolio quality, beating elite VCs (3.51%) and outperforming solo angels (1.50%) by 160%. Multi-stage architectures multiply quality by *complementing* stages (sourcing scouts → AI filter → expert committee), not adding to them. Selection consistency (CV) is a third performance dimension alongside quality and scale; platform architectures achieve CV < 0.10 vs. CV > 0.30 for traditional VCs.

**Formal objects.** Inherits the perception model from P1 but writes it as `logit(q̂ᵢⱼ) = logit(θᵢ) + xᵢᵀβⱼ + εᵢⱼ` — note **drift from q to θ** in P2 line 113. Defines portfolio success `P(success) = 1 − (1 − p̄)ⁿ`, sequential vs. batch error decomposition (`ε_seq = σ²_threshold + σ²_perception + σ²_temporal` vs. `ε_batch = σ²_perception / √n_compared`), correlated committee variance `Var(q̂_committee) = β²σ²_features + σ²_noise(1 + (m−1)ρ)/m`, and a multi-stage complementarity result `ΔQuality = (I₂/I_total) · log(n₁/n₂) · (1 − ρ_stages)` showing stage gains compound multiplicatively when stages are uncorrelated.

**Evidence.** PRISM (Progressive Refinement in Selection Modeling) — a Monte Carlo framework with a 4-tier candidate-quality distribution (1% exceptional, 9% strong, 30% moderate, 60% weak) and 11 evaluator archetypes. Pitch-sensitivity β ~ N(0.75, 0.15), profile bias on [0, 1] with 30% zeroed, noise σ ~ 0.5.

**Code artifacts.**
- Source: [pitch_review_simulation/simulation.py](pitch_review_simulation/simulation.py) (~1,250 lines, canonical PRISM implementation).
- Cleaned: [code/paper2_simulation/simulation.py](code/paper2_simulation/simulation.py) and [code/paper2_simulation/run_all_archetypes.py](code/paper2_simulation/run_all_archetypes.py).
- Sensitivity sub-experiment: [code/paper2_simulation/ai_sensitivity.py](code/paper2_simulation/ai_sensitivity.py) — closes the P2↔P3 seam.
- Stale: angels.ipynb / vc.ipynb / vectorized.ipynb / pitch_review_simulation_full.ipynb — superseded; will be marked in a `STALE.md`.
- Results CSVs: 12 `results_*.csv` pairs in [pitch_review_simulation/](pitch_review_simulation/), to be migrated to [code/paper2_simulation/results/](code/paper2_simulation/results/) with normalized archetype numbering. The `results_9_cyrannus_*.csv` files are duplicates of `results_6_cyrannus_*.csv` — drop one.

**Open issues.** P2 idealizes the AI-filter stage (β ≈ 0); Paper 3 measures real LLM noise empirically and the two have not been reconciled. The 4-tier quality distribution is asserted but never validated against real platform data. "[Suggested Figure …]" placeholders remain in the prose. The `θ` vs `q` notation drift from P1 should be resolved.

### 3.3 Paper 3 — Instruction Distillation for Startup Pitch Ranking

**Claim.** <!-- PUBLIC --> LLMs configured via *instruction distillation* (reverse-engineering evaluation criteria from existing expert reviews rather than soliciting them directly) can serve as scalable first-pass filters that align with human expert rankings at NDCG@20 = 0.923. The best single configuration — Setup 1 (component-based, four criteria: market potential, solution viability, team capability, initial traction) with the Anthropic model — reaches NDCG@10 = 0.908. Ensemble averaging across all setups raises NDCG@10 to 0.924. The system removes presentation-polish bias by separating *pitch quality* from *startup quality*, and reduces expert workload by ~50%.

**Formal objects.** No new formalism; Paper 3 is empirical. Uses NDCG@{10, 20, 35} as the ranking metric. Defines four prompting setups: Setup 1 (component-based, 4-criterion structured), Setup 2 (guided methodology), Setup 3 (chain-of-thought), Setup 4 (minimal). Two models: Anthropic (Claude), OpenAI (GPT-4). Two runs per (setup, model). Score aggregation per startup is the weighted average of the four component scores in Setup 1.

**Evidence.** 35 anonymized startups from the Cyrannus platform, each with averaged expert ranking as ground truth. Headline tables (paper §5.1.2): per-setup NDCG (Table 2), averaged-runs NDCG (Table 3), averaging-strategies NDCG (Table 4). Table 4 row "avg (all setups)": NDCG@10 = 0.923787, NDCG@20 = 0.922836, NDCG@35 = 0.976521.

**Code artifacts.**
- Source pipeline: [pitch_review/pitch_test_claude.py](pitch_review/pitch_test_claude.py) (Anthropic) and [pitch_review/pitch_test_openai.ipynb](pitch_review/pitch_test_openai.ipynb) (OpenAI).
- Source results: six `simple_*_pitch_test_*.ipynb` files in [pitch_review/](pitch_review/) — one per (setup, model) variant. Their per-setup outputs were collated into [pitch_review/ratings_full.csv](pitch_review/ratings_full.csv) (36×17) and [pitch_review/ratings_results_and_averages.csv](pitch_review/ratings_results_and_averages.csv) (35×29).
- Cleaned: [code/paper3_llm_eval/pitch_evaluator.py](code/paper3_llm_eval/pitch_evaluator.py), [code/paper3_llm_eval/run_experiments.py](code/paper3_llm_eval/run_experiments.py), [code/paper3_llm_eval/aggregate_ndcg.py](code/paper3_llm_eval/aggregate_ndcg.py).
- Anonymized data: [code/data/ai_reviews_research_anon.csv](code/data/ai_reviews_research_anon.csv) — direct input to `aggregate_ndcg.py`. NDCG values from this file should reproduce the paper's tables exactly.

**Open issues.** Paper claims N = 40 but the canonical results file has 34 distinct startups (one row appears tied). Either reconcile N = 34 or document the 6-startup exclusion. Six near-duplicate "simple_*" notebooks should be collapsed into a single orchestrator. The moderation pipeline has three versioned notebooks (`moderation_pipline.ipynb`, `_v1`, `_v2` — note the `pipline` typo); decide whether the paper relies on it.

## 4. Shared formalism — symbol audit

| Symbol | Definition | P1 usage | P2 usage | P3 usage | Drift to fix |
|---|---|---|---|---|---|
| **q** | True quality / success probability | ✓ (§0 symbol table, body) | uses **θ** instead (line 113, 117, 316, 324, 332, 340, 1128) | n/a (empirical) | **P2 → q** to match P1 |
| **q̂** | Perceived quality | ✓ | ✓ | implicit (LLM scores) | OK |
| **β** | Systematic bias vector | ✓ (vector) | ✓ but split into `β_pitch`, `β_profile` scalars (§3.1) | implicit | Document the vector→scalar specialization in P2 §3.1 |
| **ε** | Random noise | ✓ | ✓ | implicit (LLM stochasticity) | OK |
| **x** | Observable feature vector | ✓ | ✓ | implicit (the four AI criteria are the observed features) | OK |
| **k** | Committee size | ✓ | sometimes uses **m** (§5 committee variance) | n/a | **P2 → k** for committee size |
| **n** | Candidate pool size | ✓ | ✓ | n/a | OK |
| **ρ_β, ρ_ε** | Bias / noise correlation across evaluators | ✓ | sometimes just ρ | n/a | Disambiguate in P2 |
| **σ_AI** | AI-filter noise std | n/a | implicit (filter parameter) | n/a — but Paper 3's NDCG measures it indirectly | The sensitivity sub-experiment makes this explicit |
| **NDCG@k** | Ranking metric | n/a | n/a | ✓ | New in P3; document in trilogy index, not in P1/P2 |

P1 §0 is the canonical symbol table; everything else inherits from it.

## 5. Cross-paper consistency map

The most important gap, and the only one that materially affects published numbers:

| What P2 assumes | What P3 measures | Implication |
|---|---|---|
| AI filter stage runs at β ≈ 0 (unbiased) and small noise. | LLMs have measurable systematic bias (OpenAI shows positivity bias; Anthropic is more selective). | P2's reported platform-vs-elite-VC gap may be optimistic if real AI filters import their own bias. |
| AI filter as a single deterministic ranker. | LLM outputs are stochastic; ensemble averaging materially improves NDCG (0.908 → 0.924). | P2's filter is effectively the *ensemble*; using a single LLM run would degrade it. |
| AI filter perfectly separates from human stage. | LLMs and humans correlate strongly on transcripts but disagree on team-credential gaps and traction-evidence vagueness (P3 §5.4 error analysis). | The "stages are uncorrelated" assumption that lets stage gains multiply (P2 §5) is optimistic; this is the right place to add a ρ_stages sensitivity. |

**Resolution chosen for this cleanup pass:** add a single sensitivity sub-experiment in P2 §5 ([code/paper2_simulation/ai_sensitivity.py](code/paper2_simulation/ai_sensitivity.py)) that sweeps σ_AI over a range bracketing P3's measured value, plots platform vs. elite-VC quality as a function of σ_AI, and marks the P3 point on the curve. This preserves P2's headline numbers while showing how robust they are to realistic AI noise.

## 6. Reading order <!-- PUBLIC -->

For someone discovering the trilogy:

1. **Paper 1 §1 + §2 (Six Phenomena)** — the empirical hook. You'll recognize the patterns even if you reject the math.
2. **Paper 1 §0 + §3** — the symbol table and the perception model. Cost: 15 minutes; everything else builds on these.
3. **Paper 2 §1 + §2** — the platform paradox stated plainly with one figure. Decide here whether you care about the simulation results.
4. **Paper 3 §1 + §5.1.2 (Tables 2–4)** — the empirical demonstration that the AI stage Paper 2 hypothesizes actually works.
5. **Back to Paper 1 §4–§7** — derivations of the six phenomena now that you've seen the framework do real work.
6. **Paper 2 §5 (results) + new §5.X (AI sensitivity)** — full simulation results in context of real AI performance.

For an experienced reader who already accepts the LENS model: skip step 1 and read in order 2 → 3 → 4 → 6.

## 7. Open questions and known weaknesses

- **Paper 1 calibration is not reproducible from this repo.** Per-rater human ratings (k = 10 raters per startup) do not exist in the data; only averaged `expert_score` per startup. The published β_merit = 0.79 and β_delivery = 0.297 must have come from a feature decomposition (substantive vs. presentational) that is not present in any CSV here. Either the executor session must (a) request the missing feature definitions from the author, or (b) replace P1 §6's calibration narrative with the regression we *can* run on the AI-derived component scores in [code/data/startup_evaluations_avg_anon.csv](code/data/startup_evaluations_avg_anon.csv).
- **Sample size is small (N ≈ 34–35).** Sufficient as a proof-of-concept; insufficient for strong external validity. A larger-N replication is the obvious next paper but is explicitly out of scope for this trilogy. Each v2 paper will say so.
- **Paper 2 ↔ Paper 3 reconciliation** is partial. The sensitivity sub-experiment (above) addresses σ_AI but does not address the broader question of stage-correlation ρ_stages, which P2's multiplicative complementarity result assumes is small.
- **Paper 1 has 14 unresolved editorial NOTEs** in the source markdown. Each needs a disposition decision before P1_v2 ships.
- **Paper 3's stated N is inconsistent.** Abstract and methods say 40 startups; the canonical results table has 35 rows (and 34 distinct after de-duplication). Reconcile.
- **Citations missing in Paper 1.** Contrarian-returns claim (line 77), winner's curse origin, homophily literature.
- **The `guidelines/` folder** at the repo root contains Tycheism-project material from another project; it is not used by the LENS papers and should be moved or deleted.

## 8. Confidentiality and data availability <!-- PUBLIC -->

The underlying startup data (founder names, transcripts, contact information, S3 URIs) is confidential and is not shared. All analysis code in [code/](code/) consumes only anonymized derivatives in [code/data/](code/data/), where each startup is identified by a stable opaque ID (`S001` … `SNNN`). Anonymized rankings are sufficient to reproduce the NDCG and regression results reported in Papers 1 and 3. The original confidential CSVs in [tables/](tables/) and [pitch_review/](pitch_review/) are read-only and not part of the shared code tree.

## 9. Code-to-paper crosswalk (internal)

| Paper | Section | Code | Anonymized data | Output |
|---|---|---|---|---|
| P1 | §6 calibration | [code/paper1_calibration/calibrate_beta.py](code/paper1_calibration/calibrate_beta.py) | [code/data/startup_evaluations_avg_anon.csv](code/data/startup_evaluations_avg_anon.csv) | β coefficients printed |
| P2 | §5 Table 5.1 | [code/paper2_simulation/run_all_archetypes.py](code/paper2_simulation/run_all_archetypes.py) | (none — pure simulation) | code/paper2_simulation/results/results_*.csv |
| P2 | §5.X (NEW) AI sensitivity | [code/paper2_simulation/ai_sensitivity.py](code/paper2_simulation/ai_sensitivity.py) | [code/data/ai_reviews_research_anon.csv](code/data/ai_reviews_research_anon.csv) (for empirical anchor) | results/sensitivity_curve.{csv,png} |
| P3 | §5.1.2 Tables 2–4 | [code/paper3_llm_eval/aggregate_ndcg.py](code/paper3_llm_eval/aggregate_ndcg.py) | [code/data/ai_reviews_research_anon.csv](code/data/ai_reviews_research_anon.csv) | results/ndcg_table.csv |
| P3 | §3 (re-runs only) | [code/paper3_llm_eval/run_experiments.py](code/paper3_llm_eval/run_experiments.py) | (lives outside repo — pitch transcripts) | new per-setup CSVs |
