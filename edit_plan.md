# LENS Trilogy — Edit Plan for paper{1,2,3}_v2.md

This document is the executor's checklist. Run it in a separate session whose only job is to produce three new files alongside the originals:

- `paper1_v2.md` (next to `1 LENS_ A Mathematical Foundation for Human Decision-Systems Engineering (2).md`)
- `paper2_v2.md` (next to `2 The Platform Paradox_ When Angels with Architecture Outperform Elite VCs (1).md`)
- `paper3_v2.md` (next to `3. Instruction Distillation for Startup Pitch Ranking_ LLMs as Scalable First-Pass Filter.md`)

The originals are untouched. The companion documents — [lens_trilogy.md](lens_trilogy.md) and [code/README.md](code/README.md) — are the source of truth for shared notation and code-to-section mapping; cite them, do not duplicate.

## Operating instructions for the executor

- **Read these first**: [lens_trilogy.md](lens_trilogy.md), [code/README.md](code/README.md), and the original paper you're editing. Do not skim — the trilogy doc encodes decisions that this checklist assumes.
- **Run code, don't just read it**. Before changing a number in any paper, run the script that produces it:
  - Paper 1 §6: `/c/Users/mikea/anaconda3/python.exe code/paper1_calibration/calibrate_beta.py`
  - Paper 2 §5: `/c/Users/mikea/anaconda3/python.exe code/paper2_simulation/run_all_archetypes.py` (full, ~minutes)
  - Paper 2 §5.X (NEW): `/c/Users/mikea/anaconda3/python.exe code/paper2_simulation/ai_sensitivity.py`
  - Paper 3 §5.1.2: `/c/Users/mikea/anaconda3/python.exe code/paper3_llm_eval/aggregate_ndcg.py`
- **Use AskUserQuestion** for any ambiguity that materially changes a number or claim. Do not silently invent.
- **Confidentiality is non-negotiable**. The v2 papers reference only anonymized data under `code/data/`. No real startup names appear anywhere.
- **Sample-size framing is non-negotiable**. Each paper must include a "Limitations" sentence that frames N ≈ 34 as proof-of-concept and points to larger-N replication as out-of-scope future work.
- **Out-of-scope guard**: do not refactor the conceptual framework, add new theorems, or change the perception model. The job is editorial cleanup, not redesign.

## Global checklist (applies to all three v2 files)

- [ ] Replace any reference to `pitch_review/` or `pitch_review_simulation/` with the corresponding `code/` path (consult [code/README.md](code/README.md)'s crosswalk table).
- [ ] Use [lens_trilogy.md](lens_trilogy.md) §4 (symbol audit) as the single source of truth. Resolve any drift in favor of Paper 1's §0 symbol table.
- [ ] Add a one-paragraph **Data Availability** statement near the methods section: "The underlying startup data is confidential and is not shared. All analyses use anonymized derivatives in `code/data/`, where each startup is identified by a stable opaque ID. Anonymized rankings are sufficient to reproduce the results reported here."
- [ ] Add a **Limitations** sentence (or expand an existing one): "Our sample size (N ≈ 34) is sufficient as a proof-of-concept but insufficient for strong external validity. A larger-N replication is the natural follow-up and is out of scope for this paper."
- [ ] No real startup names anywhere (search-and-grep before saving).
- [ ] No editorial NOTEs left in prose (search for `NOTE:` and `<<` markers — see Paper 1 specifically).

---

## `paper1_v2.md` checklist

### Editorial NOTEs to resolve

Paper 1 contains 14 author NOTEs in the source markdown. Disposition decisions:

- [ ] **Line 7** (abstract): NOTE about the abstract being too example-heavy. **Decision**: rewrite the second half of the abstract to lead with the framework's *generality* (decomposition explains six unrelated phenomena) and use the six examples as keyword bait at the end. Two sentences max.
- [ ] **Line 11** (abstract): NOTE about log-odds choice. **Decision**: keep log-odds as the canonical formulation; add a one-sentence footnote acknowledging that linear or other monotone formulations are equivalent for the qualitative results, deferring formal generalization to future work. Do not multiply formulations in the body.
- [ ] **Line 53** (§0): NOTE asking whether to move §0 to an appendix. **Decision**: keep §0 up front. The symbol table grounds the reader before the six phenomena and makes the equation in §1 less abrupt.
- [ ] **Lines 61, 65, 115** (§1 intro): NOTEs about the formula being used in examples before being introduced. **Decision**: insert one short paragraph at the very start of §1 ("This paper uses the perception model logit(q̂) = logit(q) + βᵀx + ε. We motivate it via six recognizable phenomena, then derive its design implications. Readers wanting the model first can jump to §3.") and remove the inline NOTEs.
- [ ] **Line 69** (winner's curse): missing citation NOTE. **Decision**: add Capen et al. 1971 (oil-lease auctions, the canonical winner's curse paper) and Thaler 1988 (Anomalies survey).
- [ ] **Line 73** (homogeneity trap): missing-citation NOTE. **Decision**: add Castilla 2008 / Rivera 2012 (homophily in hiring) — confirm the exact paper the author intended; if unclear, AskUserQuestion.
- [ ] **Line 77** (contrarian returns): missing-citation NOTE. **Decision**: ask author for the source. If unavailable, soften the claim from "consistently generating 3-5× returns" to "with above-average reported returns" and cite Kerr et al. 2014 (Angel investing returns) or similar.
- [ ] **Lines 81, 85, 89, 97, 105**: smaller editorial NOTEs in the six-phenomena exposition. Read each, decide in context, remove the NOTE.

### Calibration (§6)

The published β_merit = 0.79 / β_delivery = 0.297 are not reproducible from this repo because per-rater human merit/delivery features are missing. Pick one of the two routes:

- [ ] **Preferred route**: Use AskUserQuestion to ask whether the merit/delivery features used to compute the published β are still on the author's machine. If yes, request the exact feature definitions (and the data file if anonymizable) so the regression can be re-run and either confirmed or corrected.
- [ ] **Fallback route** (if author cannot supply): Replace §6's calibration narrative with the AI-component regression that `code/paper1_calibration/calibrate_beta.py` produces (β[market_potential] ≈ 0.95, β[team_capability] ≈ 0.26, R² ≈ 0.75). Reframe §6 as "the LENS perception model fits the data with R² ≈ 0.75 even when AI-derived component scores stand in for the original human merit/delivery judgments." Update the abstract's β values accordingly (or remove specific numbers from the abstract).

### Appendices

- [ ] Verify Appendix A, B, C are referenced in the body. If yes, add their content (or, more honestly, remove the references — most "Appendix A" mentions in the source appear placeholder-ish).

### Content-level

- [ ] Add the Data Availability paragraph (see Global).
- [ ] Add the Limitations sentence (see Global). For Paper 1 specifically, frame N = 35 as a *single* calibration point that demonstrates the model fits, not as evidence the framework is universally true.
- [ ] Add forward-pointers to companion papers wherever §1 currently says "comprehensive validation appears in companion papers" — name them explicitly: "validated empirically in Paper 2 (simulation) and Paper 3 (real LLM-as-AI-filter)."

---

## `paper2_v2.md` checklist

### Notation drift

- [ ] Search for **θ** (line 113, 117, 316, 324, 332, 340, 1128) and replace with **q** to match Paper 1 §0. Verify the equation `logit(q̂ᵢⱼ) = logit(θᵢ) + xᵢᵀβⱼ + εᵢⱼ` becomes `logit(q̂ᵢⱼ) = logit(qᵢ) + xᵢᵀβⱼ + εᵢⱼ`.
- [ ] Search for committee size **m** in §5 committee-variance discussion; replace with **k** to match Paper 1.
- [ ] β_pitch and β_profile: keep the scalar specialization (it's domain-specific and clearer than the vector form for VC examples) but add one sentence in §3.1 explaining "β = (β_pitch, β_profile) is the two-component specialization of Paper 1's bias vector."

### New subsection: §5.X "AI Filter Sensitivity"

- [ ] Add this subsection after §5's main results table. Length: ~½ page + 1 figure.
- [ ] Embed the figure produced by [code/paper2_simulation/ai_sensitivity.py](code/paper2_simulation/ai_sensitivity.py) at `code/paper2_simulation/results/sensitivity_curve.png`.
- [ ] Sample text frame:
  > "Our headline platform-vs-elite-VC comparison treats the AI filter as effectively unbiased and low-noise. Paper 3 measures real LLM performance, which corresponds to a finite σ_AI. Figure X sweeps σ_AI across [0, 0.6] (the range bracketing Paper 3's measured value, σ_AI ≈ 0.35) and reports platform mean portfolio quality at each point. The platform's quality is robust to AI noise within this range; the platform-vs-elite gap is driven primarily by architecture (multi-stage vs. single-evaluator), not by AI infallibility."
- [ ] **Verify the headline numbers reproduce.** The smoke run during cleanup found that with default `simulation.py` parameters and 200 trials, the cyrannus_ai_20 and elite_vc archetypes both score around 3.46–3.48% — *not* the reported 3.91% vs. 3.51%. Either:
  - re-run `run_all_archetypes.py` at full trial count (1000+) and confirm the original numbers, or
  - if the gap doesn't reproduce, soften the headline to match what the simulation actually produces, or
  - identify the specific platform configuration in INVESTOR_CONFIGS that produces the 3.91% number (the executor must read `simulation.py` to find it; it is *not* `cyrannus` or `cyrannus_ai_20`).

### Parameter consistency

- [ ] §3.1 lists pitch sensitivity β_pitch ~ N(0.75, 0.15), profile bias on [0, 1] with 30% zeroed, noise σ ~ 0.5. Cross-check against the actual values in `code/paper2_simulation/simulation.py` (search for `noise_std`, `pitch_sensitivity`, `profile_bias`). If they differ per archetype, add a footnote acknowledging that the headline values are population means and per-archetype overrides exist (cf. `bias_overrides` in `INVESTOR_CONFIGS`).

### Figure placeholders

- [ ] Search for "Suggested Figure" or "[Figure" placeholders. For each: either embed the matching PNG from `code/paper2_simulation/results/` (or move from `pitch_review_simulation/`), or remove the placeholder.

### Cross-references and content

- [ ] Add a forward-pointer to Paper 3 in the AI-filter discussion: "Paper 3 instantiates this AI-filter stage with real LLMs and measures NDCG@20 = 0.923 against expert consensus."
- [ ] Add the Data Availability paragraph (see Global).
- [ ] Add the Limitations sentence (see Global). For Paper 2 specifically, note that the 4-tier candidate-quality distribution is asserted, not validated against real platform data.

---

## `paper3_v2.md` checklist

### Reconcile N

- [ ] Paper claims N = 40 startups; canonical results table has 35 rows (and 34 distinct names). Preferred resolution: correct the prose to N = 34 (or N = 35 if one row is intentional duplicate) and add one sentence stating the table is the authoritative count. Alternatively, document the 6-startup exclusion explicitly and identify why those startups were dropped.

### Reconcile setups

- [ ] Paper 3 §3 lists 4 setups (s1 component, s2 guided, s3 chain-of-thought, s4 minimal). The canonical results table contains s1, s2, s4 — **s3 is missing**. Resolution options:
  - re-run s3 using [code/paper3_llm_eval/run_experiments.py](code/paper3_llm_eval/run_experiments.py) and the prompt template at [code/paper3_llm_eval/prompts/setup3_cot.py](code/paper3_llm_eval/prompts/setup3_cot.py) (requires API keys), or
  - reduce the prose to 3 setups and note that chain-of-thought was tried but not retained for the final analysis.

### Reproduce Tables 2–4

- [ ] Run [code/paper3_llm_eval/aggregate_ndcg.py](code/paper3_llm_eval/aggregate_ndcg.py). Compare its output (`code/paper3_llm_eval/results/table*.csv`) against the paper's published Table 2, 3, 4 numbers.
- [ ] **Encoding choice**: the paper's Table 4 numbers (avg @10/@20/@35 = 0.924/0.923/0.977) match `aggregate_ndcg.py` under **exponential gain** (`2^rel - 1`), not linear gain. State the gain function explicitly in §3 ("We use exponential-gain NDCG: gain_i = 2^expert_score_i − 1.") and verify all reported numbers were computed with this encoding.
- [ ] If a paper number doesn't reproduce within 0.005, fix the paper number (the script is authoritative); if it differs by more than 0.01, investigate before changing anything.

### Cross-references

- [ ] Add a backward-pointer to Paper 2's new §5.X: "These measured values correspond to σ_AI ≈ 0.35 on the sensitivity curve in Paper 2 §5.X, indicating the platform-architecture conclusions are robust to realistic AI performance."
- [ ] Replace any "see notebook X" reference with `code/paper3_llm_eval/...` paths.

### Other content

- [ ] Strengthen §6 limitations: small N is sufficient for proof-of-concept (NDCG@20 = 0.923 is a real signal at this N) but insufficient for generalization. Explicit larger-N replication is the natural follow-up paper. Frame as future work, not as a defect.
- [ ] Decide on the moderation pipeline: skim §6 and decide whether the paper depends on it. If yes, port the canonical version (latest of `pitch_review/moderation_pipline_v2.ipynb`) into `code/paper3_llm_eval/`. If no, remove any §6 references to it.
- [ ] Add the Data Availability paragraph (see Global).

---

## Verification block

Before declaring each `paper*_v2.md` done:

1. **No editorial NOTEs**: `grep -E "(NOTE:|<<|TODO|FIXME)" paperN_v2.md` returns nothing.
2. **No real startup names**: cross-reference against `tables/_private/name_to_id_map.csv`; none of those 117 names appears in any v2 paper.
3. **All code references resolve**: every `code/...` path mentioned in the v2 paper exists.
4. **Symbol consistency with [lens_trilogy.md](lens_trilogy.md) §4**: spot-check three equations.
5. **Numbers reproduce**: re-run the relevant script and confirm any number quoted in the paper matches its output (within rounding).
6. **Limitations / Data Availability paragraphs present**.

When all three v2 papers pass, the trilogy cleanup is complete.

---

## What the executor should NOT do

- **Do not** modify the original `.md` files. Originals stay untouched.
- **Do not** modify any file under `tables/` or `pitch_review/` or `pitch_review_simulation/`. The cleanup pass already added `STALE.md` markers; the v2 editor doesn't extend them.
- **Do not** redesign the perception model, add new theorems, or restructure §s of the papers beyond what this checklist names.
- **Do not** delete the `guidelines/` folder — that's a separate decision the user makes after reviewing.
- **Do not** initialize a git repo without the user asking. The plan deliberately chose v2-alongside-originals to avoid that decision.
- **Do not** push code to any remote, run anything that hits paid APIs at scale, or modify shared infrastructure.

If anything is unclear, AskUserQuestion. Do not invent.
