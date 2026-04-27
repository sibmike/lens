# Instruction Distillation for Startup Pitch Ranking: LLMs as a Scalable First-Pass Filter

**Mikhail L. Arbuzov, Lee Mosbacker**

*Cyrannus Inc., 2025. Third paper in the LENS trilogy. Paper 1 introduces the perception-model framework. Paper 2 demonstrates through Monte Carlo simulation that selection architecture beats individual evaluator skill. This paper instantiates Paper 2's idealized AI-filter stage in a working system: a large language model, prompted via instruction distillation, ranks one-minute startup pitches in alignment with a ten-expert crowd at NDCG@20 = 0.923.*

---

## Abstract

Early-stage venture screening has a structural problem. Expert reviewers are scarce; pitch volume is not. The reviewers who do read pitches are demonstrably influenced by presentation polish — charisma, fluency, slide design — rather than by the substance the pitch is supposed to convey, and that influence persists even when reviews are aggregated across a panel. The result is a screening process that consumes the costliest input (expert time) on the cheapest signal (pitch craft).

This paper shows that a large language model can do most of the pitch-craft filtering and leave the substantive evaluation to humans. We rank 35 anonymized startup pitches from the Cyrannus platform under four prompting strategies and two model providers (Anthropic Claude, OpenAI GPT-4), with a ten-expert consensus as ground truth. The component-based prompt with Claude reaches NDCG@10 = 0.908 on a single run; ensemble averaging across all available prompt strategies reaches NDCG@20 = 0.923. The model never replaces the expert; it eliminates the obviously unsuitable pitches and frees the expert to evaluate substance.

The methodological contribution is *instruction distillation*: rather than asking experts to articulate their criteria — which they typically cannot do precisely — we have an LLM read pairs of (pitch, expert review) and reverse-engineer the implicit rubric the panel was applying. The result is a structured prompt that captures the panel's collective methodology without requiring any expert to write it down.

> **Data availability.** Underlying startup data is confidential. All analyses use anonymized derivatives in [`code/data/`](../code/data/). The script that reproduces every NDCG number in this paper is [`code/paper3_llm_eval/aggregate_ndcg.py`](../code/paper3_llm_eval/aggregate_ndcg.py).
>
> **Sample size.** N = 35 is sufficient as a proof-of-concept that the approach produces a real signal — NDCG@20 = 0.923 against a ten-expert ground truth is not noise at this N — but it is insufficient for strong external validity. A larger-N replication is the natural follow-up paper and is out of scope here.

**Keywords:** venture capital, startup screening, large language models, instruction distillation, NDCG, AI-augmented evaluation, scalable expert review.

---

## 1. The Problem

The early-stage venture process at every well-known platform looks roughly the same. A pool of applicants is reduced to a top fraction through one or two rounds of expert review, and the survivors enter due diligence. The expert review is where the bottleneck lives. Each pitch demands real cognitive work, the experts are scarce, and the work does not scale: doubling the applicant pool roughly doubles the expert hours required to maintain the same selection quality.

The bottleneck is not the only problem. The expert review is also systematically biased toward presentation. A polished founder with a clean narrative gets credit for a business that the same expert, reading the same content in plainer form, might rate lower. A team with strong fundamentals but a stumbling speaker gets penalized for the stumble. This is well-documented across the entrepreneurship literature; the most pointed result is from Brooks et al. (2014), who found identical pitches scored substantially higher when delivered by attractive men. Pollack et al. (2012) document the broader pattern. Clark (2008) names the underlying confound: *pitch quality* (how well the founder communicated) is observable; *startup quality* (whether the business will work) is what investors actually want, and the two get conflated under time pressure.

Aggregating across a panel does not fix this. A ten-person committee reduces random disagreement, but if every member is susceptible to the same pitch-quality cue — and they are — the aggregate score still reflects the cue rather than the substance. This is the committee paradox of Paper 1: averaging cancels noise, not correlated bias. The fix has to come from architecture, not from adding more reviewers.

The architectural opening is that pitch quality is the cheap thing to filter on. A large language model can read a transcript and tell whether the founder named a market, named a number, named a credential, named a customer. That is not the question of whether the business will work — that question requires domain expertise the model does not have. But it *is* the question of whether the pitch contains the basic content an expert would otherwise have to extract from polish. If the model can be made to filter on substantive content rather than on the polish that wraps it, it does the work the expert is currently spending most of their time on, leaving the expert to evaluate the things the model cannot.

This paper shows that an LLM can be made to do that filtering at NDCG@20 = 0.923 against a ten-expert ground truth. The body of the paper develops the methodology, presents the empirical results, and unpacks the error analysis — the cases where the model and the expert disagree, which are themselves informative about what each is doing.

---

## 2. Background and Position in the Literature

The relevant literature splits along two dimensions: prior work on AI in venture screening (which is sparse and oriented toward later-stage companies with quantifiable metrics), and prior work on LLM-as-evaluator more generally (which is much richer but rarely targeted at ranking under expert ground truth).

The early-stage problem has been mostly closed to algorithmic methods because the inputs are unstructured and the outcome is observable only on a multi-year lag. Bernstein, Korteweg & Laws (2017) and Cumming & Groh (2018) document that data-driven methods in VC have concentrated on later-stage decisions where revenue and growth provide structured signal. Earlier attempts at NLP-based screening (Tam & Kiang, 2012; Serrano, 2010; Hochberg, Ljungqvist & Lu, 2007) used narrow training sets or rule-based pipelines with limited capacity for the qualitative judgment early-stage evaluation requires. More recent work has moved toward unstructured text: Maarouf, Feuerriegel & Pröllochs (2024) combine textual self-descriptions with structured features to predict startup success at scale on Crunchbase data, and Yankov, Ruskov & Haralampiev (2014) score on team and market dimensions to predict five-year survival. These are predictive models trained on outcome labels; they do not address the screening-stage problem of ranking pitches against an expert panel before any outcome is observable.

LLMs change what is possible at the screening stage because they can do the qualitative reading that earlier NLP could not. Brown et al. (2020) and OpenAI (2023) document the general jump in capability; Davenport & Ronanki (2018) survey the practical implications across business domains. But LLMs are not domain experts. They cannot replicate the pattern recognition of an investor who has seen a thousand decks; what they can do, reliably, is identify whether the surface content of a pitch contains what an expert would look for. Bender et al. (2021) is the canonical caveat: models fluent in form are not necessarily competent in substance, and the right deployment treats them as scalable filters rather than as autonomous decision-makers.

Chiang & Yin (2021) is the closest methodological precedent: people defer to a model appropriately when they understand its limits and adjust reliance accordingly. That framing — the model as a calibrated filter, the expert as the final decision-maker, with the architectural property that the model never sees a pitch the expert will not also see — is the framing this paper inherits. The contribution is not "LLMs can rank pitches" in isolation; it is that an LLM filter, prompted with a methodology distilled from the expert panel itself, can do the pitch-quality work at scale and free the expert to do startup-quality work where their judgment actually adds value.

The hybrid evaluation framing has been argued for in the broader AI-in-investment literature (Deloitte, 2021), but the published industry tools (Kamps, 2023, is the recent example) target founders rather than investors and are proprietary in their criteria. To the authors' knowledge, no prior work reports a system that systematically ranks startup pitches against an expert-crowd ground truth in a multi-stage screening pipeline. That is the gap this paper fills.

---

## 3. Methodology

### 3.1 The Cyrannus Pipeline and the Sample

This study runs against the Cyrannus platform's existing screening process. Founders submit one-minute video pitches. A panel of at least ten independent expert reviewers — drawn from a larger pool of more than fifty domain specialists — scores each pitch using their own rubric, blind to one another's scores. The aggregate of those scores is the pitch's ranking; the top fraction advances to due diligence, where a larger panel evaluates additional materials, and only the top few percent receive investment offers. Experts are incentivized through equity stakes in funded startups, which is the closest available approximation to skin-in-the-game evaluation at the screening stage.

We took 35 anonymized startups from this pipeline as the evaluation sample. (The original collection was 40; five were excluded for incomplete transcripts or for moderation flags on the underlying video. The exclusion is a bookkeeping decision, not a selection on outcome.) These startups were actively raising their first funding round at the time of evaluation. They sit at the technological frontier in their respective verticals — fintech, healthcare, enterprise software, consumer technology — which means there was no published outcome data for the LLM to leak from prior training. Each startup had received scores from at least ten expert reviewers, and the aggregate of those scores is the ground truth this paper benchmarks against.

The sample is small. N = 35 is enough to demonstrate that a methodology produces a real signal — 0.923 against a ten-expert ground truth is not noise at this size — but it is not enough to support strong external generalizations. A larger replication is the obvious next paper. We say this once, here, rather than threading the caveat through the rest of the document.

### 3.2 Instruction Distillation

The core methodological move is how the LLM is given its evaluation criteria. The standard approach — interview experts, write a rubric, hand the rubric to the model — fails twice over. Experts cannot articulate their criteria precisely; what they tell you in an interview is a rationalization of what they are actually doing. And even when they can, ten experts produce ten different rubrics, none of which represents the consensus the aggregate score reflects.

Instruction distillation reverses the direction. We give the LLM pairs of (pitch transcript, expert review) and ask it to produce a structured analysis of each pitch — what the expert noticed, what the expert seemed to weight, where the pitch fell short, what an improvement would look like. The LLM is now doing the rationalization, but it is doing it on observed data rather than on memory. After several dozen of these analyses, we have the LLM read across them and extract the patterns: which features recur as drivers of high scores, which recur as drivers of low scores, what the implicit weighting looks like. The output of this second pass is a methodology document — a structured prompt, in the language the LLM speaks — that captures the panel's collective rubric without any expert having had to write it down.

This is *instruction distillation*. The name is a deliberate echo of model distillation (training a small model to imitate a large one), but the object distilled is not a network; it is a procedure. The distilled methodology is then used as a system prompt in the actual ranking experiments, which is what the rest of this paper measures.

The distilled methodology resolved into four assessment criteria the panel was implicitly weighting: market potential (the clarity and significance of the problem and the size of the addressable market), solution viability (whether the proposed solution makes logical sense and has competitive defensibility), team capability (whether the founders' backgrounds map credibly onto what the venture requires), and initial traction (whether there is concrete evidence of validation — users, revenue, partnerships, or pilot results). Each criterion came with specific evaluation questions derived from the patterns the LLM identified across the (pitch, review) pairs.

### 3.3 The Four Prompting Setups

To isolate which features of the prompt actually drive ranking quality, we tested four prompting strategies of increasing structure. We label them s1 through s4 in the order they appear in the results tables; describing them in increasing order of scaffolding makes the comparison interpretable.

The least-structured setup (s4, "minimal guidance") gives the model the pitch transcript, the role of "venture scout," and a one-to-five rating scale, and asks for a single overall score with a confidence rating. There is no methodology, no chain-of-thought, no decomposition. This is the no-scaffolding baseline against which every other setup is compared.

The chain-of-thought setup (s3) adds an explicit instruction to reason step-by-step before scoring: walk through market, solution, team, traction; identify the strongest and weakest aspects of the pitch; then assign the rating. The setup tests whether the act of forcing intermediate reasoning improves final ranking quality. As we discuss below, the canonical results table for this paper does not include s3 data, due to a logging error during the experiment run; the prompt itself is preserved in the supplementary materials and the experiment is straightforward to replicate.

The guided-methodology setup (s2) drops the full distilled methodology into the prompt and asks the model to produce a single overall score using the methodology as system context. This is the setup that tests whether the methodology helps when it is provided as a single document rather than enforced through structural decomposition.

The component-based setup (s1) is the most structured. It runs four separate LLM calls per pitch, one per criterion, each with its own copy of the methodology focused on the one criterion under evaluation. The four scores are then combined via a weighted average. The decomposition is the architectural prediction from Paper 1 brought into the prompt: separate evaluation reduces the tendency for one cue to dominate the others.

Two model providers were used for each setup: Anthropic's Claude and OpenAI's GPT-4. Each (setup, model) combination was run twice to allow ensemble averaging. The result is up to sixteen score columns per startup (four setups × two models × two runs), against the ten-expert aggregate as ground truth. The complete prompts live in [`code/paper3_llm_eval/prompts/`](../code/paper3_llm_eval/prompts/).

### 3.4 Evaluation Metric

We report Normalized Discounted Cumulative Gain at three cutoffs: NDCG@10, NDCG@20, NDCG@35. NDCG penalizes ranking errors more heavily near the top of the list, which is the right shape for an investment-screening problem where the top of the ranking is what actually gets acted on. We use the exponential-gain formulation, $\mathrm{gain}_i = 2^{\mathrm{expert\_score}_i} - 1$, with a $\log_2(\mathrm{rank} + 1)$ discount. The reproduction script is [`code/paper3_llm_eval/aggregate_ndcg.py`](../code/paper3_llm_eval/aggregate_ndcg.py); every NDCG number in this paper comes from running it against [`code/data/ai_reviews_research_anon.csv`](../code/data/ai_reviews_research_anon.csv).

We also report precision and recall at the top-20 cutoff, treating the expert top-20 as the positive class. These are easier to interpret operationally — they tell an investor what fraction of the LLM's top-20 they would have chosen anyway, and what fraction of their own picks the LLM identifies — and they correlate strongly with NDCG without replacing it.

---

## 4. Results

### 4.1 Score Distribution and Model-Provider Differences

Before discussing rankings, the scores themselves carry a finding: when the model has no methodology to anchor against, both providers compress their score distributions, but they compress in different ways. OpenAI without a methodology assigns a score of four to roughly eighty percent of the pitches, which is functionally a refusal to differentiate. Anthropic without a methodology spreads the scores more, but still less than under the structured setups. Adding the distilled methodology spreads both distributions to something closer to what the human expert panel produced — wider, with meaningful mass at the lower scores.

The implication is that prompt structure is doing more than guiding the model's reasoning; it is also overriding a default tendency toward positivity, especially for OpenAI. This is consistent with the broader observation that models trained with instruction-following and helpfulness objectives are biased toward agreeable outputs, and that it takes deliberate prompt engineering to extract honest negative judgments. For the specific application of pitch ranking, the practical consequence is that any single-model deployment needs to be score-normalized before its outputs are comparable to a human panel.

### 4.2 Ranking Accuracy

The headline result is that the component-based setup (s1) with Anthropic reaches NDCG@10 = 0.908 on a single run — strong alignment with the expert panel for the part of the ranking that actually drives investment decisions. Table 1 reports NDCG at three cutoffs for every (setup, model) combination for which canonical per-startup data is preserved. As noted above, the s3 (chain-of-thought) cells are absent due to a logging error during the experiment run; the script for re-running them is in [`code/paper3_llm_eval/run_experiments.py`](../code/paper3_llm_eval/run_experiments.py).

**Table 1.** NDCG against the ten-expert aggregate, single run per cell.

| Setup | Model | NDCG@10 | NDCG@20 | NDCG@35 |
| --- | --- | --- | --- | --- |
| s1 (component) | Anthropic | 0.908 | 0.901 | 0.971 |
| s1 (component) | OpenAI | 0.881 | 0.897 | 0.967 |
| s2 (guided) | Anthropic | 0.856 | 0.873 | 0.950 |
| s2 (guided) | OpenAI | 0.696 | 0.782 | 0.895 |
| s4 (minimal) | Anthropic | 0.842 | 0.884 | 0.958 |
| s4 (minimal) | OpenAI | 0.786 | 0.831 | 0.939 |

Two patterns are worth pulling out. First, the component-based decomposition reliably beats the single-pass setups on Anthropic, which is the prediction Paper 1 makes about evaluator architecture brought down to the prompt level: separate evaluation reduces single-cue dominance. Second, the minimal-guidance setup beats the guided-methodology setup at the larger cutoffs (NDCG@20 and NDCG@35), which suggests the model has a non-trivial native ability to differentiate weak from strong pitches that the structured methodology partially overrides. The methodology helps at the top of the ranking, where precision matters most; it is roughly neutral or slightly harmful in the middle, where the model's defaults are doing useful work.

Across providers, OpenAI underperforms Anthropic on every setup except component-based, and even there only by a small margin. The score-compression effect described above is the most likely cause: a model that gives most pitches a four cannot rank them.

### 4.3 Ensemble Averaging

LLM outputs are stochastic: the same prompt run twice produces slightly different scores. Averaging across runs reduces that stochasticity in the same way committee aggregation reduces individual evaluator noise — in fact, it is the same algebra ($\mathrm{Var}(\bar X) = \sigma^2 / n$ for independent draws) applied at the prompt level rather than the evaluator level.

Run-averaging within a single (setup, model) cell produces consistent improvement across the board. Table 2 reports the within-cell averages.

**Table 2.** NDCG averaged across two runs per (setup, model).

| Setup | Model | NDCG@10 | NDCG@20 | NDCG@35 |
| --- | --- | --- | --- | --- |
| s1 (component) | Anthropic | 0.916 | 0.904 | 0.976 |
| s1 (component) | OpenAI | 0.967 | 0.957 | 0.987 |
| s2 (guided) | Anthropic | 0.849 | 0.853 | 0.936 |
| s2 (guided) | OpenAI | 0.997 | 0.993 | 0.998 |
| s4 (minimal) | Anthropic | 0.882 | 0.903 | 0.969 |
| s4 (minimal) | OpenAI | 0.992 | 0.994 | 0.996 |

The largest improvements are on OpenAI, which is consistent with the score-compression diagnosis: averaging two compressed distributions adds back some of the differentiation that single runs lacked.

The strongest result comes from averaging across all setups rather than within a single setup. Table 3 reports three averaging strategies.

**Table 3.** NDCG by averaging strategy. The "all setups" row corresponds to averaging every per-startup score in the preserved data.

| Strategy | NDCG@10 | NDCG@20 | NDCG@35 |
| --- | --- | --- | --- |
| Average across all setups | 0.924 | 0.923 | 0.977 |
| Methodology-guided setups only | 0.908 | 0.905 | 0.977 |
| No-methodology setups only | 0.905 | 0.918 | 0.974 |

NDCG@20 = 0.923 against a ten-expert aggregate is the headline number. It is also striking that the no-methodology average performs comparably to the methodology-guided average at the larger cutoffs, which reinforces the §4.2 observation that the model's defaults are doing useful work. The methodology adds value at the very top of the ranking, where the precision of NDCG@10 matters most; it does not appear necessary for getting the broad shape of the ranking right.

### 4.4 Selection Quality at the Top Cutoffs

Beyond the aggregate metric, the question that matters for a deployed system is: given the top-20 pitches the LLM ranks, how many are also in the expert top-20? Across the strongest configurations, the overlap is consistently high. Most pitches that the experts placed in the bottom half of the ranking are also placed in the bottom half by the LLM — the system reliably identifies obviously unsuitable candidates, which is the part of the work that absorbs the most expert time at the screening stage. The disagreements concentrate at the top, where ranking is subtle, and that is where human judgment was always going to dominate.

### 4.5 Error Analysis

The disagreements between the LLM and the expert panel are themselves informative. Across the cases where the LLM rated a pitch substantially lower than the expert panel did, four patterns recurred consistently.

The most common was insufficient team information. Pitches that asserted relevant expertise without naming specific roles, prior employers, or directly applicable experience scored low on team capability. The expert panel, drawing on domain knowledge, was sometimes able to fill in the gap — recognizing the founder's prior company by name, knowing the role implied a particular skill set — and the LLM, lacking that domain background, could not. This is a real limitation: the LLM evaluates what the pitch contains, not what the expert can infer.

The second was limited traction evidence. Pitches that mentioned "discussions" or "interest" without quantified metrics (users, revenue, partnerships, growth rates) consistently scored lower from the LLM than from the panel. The LLM treats unsupported assertions skeptically; experienced investors are sometimes willing to trust an experienced founder's read of the market even without numbers.

The third was vague solution detail. Pitches that described what their technology *did* without describing how it differed from existing solutions or how it integrated with existing systems received lower solution-viability scores from the LLM. Experts could often guess at the differentiation from context; the LLM could not.

The fourth was market-analysis gaps. Pitches that asserted a large market without naming a specific TAM figure, a competitive landscape, a go-to-market plan, or evidence of customer willingness to pay were marked down on market potential. Again, experts sometimes filled in the missing pieces from prior knowledge of the sector.

These four patterns have a common shape: the LLM is a strict reader of what the pitch contains; the expert is a generous reader who can supplement from domain knowledge. From a screening-system perspective, the strict reading is mostly the right behavior. A startup whose pitch does not name its TAM, its team's relevant experience, its traction metrics, or its competitive positioning is asking the screener to do work the founder should have done. The model demanding evidence rather than accepting assertion is a feature, not a bug — it pushes the work back to the founder, where it belongs.

The practical implication is that the same content that improves an LLM's ranking also improves the pitch's reception by careful human reviewers. The error analysis is not just about the model; it is also about what makes a pitch well-formed in the first place.

---

## 5. Discussion

### 5.1 What the Result Means for the Screening Bottleneck

The expert-time bottleneck at the screening stage of venture capital has a specific shape: most of the time spent reading a pitch is spent extracting basic content from presentation, and only a small fraction is spent evaluating whether the underlying business will work. The LLM filter inverts that ratio. If the model can be trusted to handle the content extraction at NDCG@20 = 0.923 alignment with a ten-expert aggregate, the experts are freed to spend their limited time on the part of the evaluation where their judgment cannot be replicated: assessing whether the team can actually execute, whether the market timing is right, whether the technical risk is manageable, whether the founder is the kind of person who will figure it out. Those are the questions the LLM cannot answer. They are also the questions that actually predict outcomes.

The architectural framing matters. The LLM is not deciding which startups to fund. It is filtering for whether a pitch contains the substantive content an expert would otherwise have to extract, and reordering the queue so that the top of the human reviewer's list is more likely to be pitches the human would have prioritized anyway. The expert remains the decision-maker. The model is a stage-zero filter that operates on observable surface content and frees the next stage to focus on substance.

This is the operational instantiation of Paper 2's "AI filter" stage. Paper 2 modeled that stage as an idealized low-noise, low-bias filter and showed that platforms with such a filter outperformed elite VCs by 11.5% on portfolio quality. This paper measures what the real version of that filter actually achieves; the σ_AI calibration in Paper 2's §5.7 sensitivity analysis is the bridge.

### 5.2 The Generalizability of Instruction Distillation

The instruction-distillation methodology is the part of this paper most likely to transfer outside venture capital. Anywhere a domain expert produces a judgment they cannot fully articulate — grant review, academic admissions, manuscript triage at a journal, candidate screening at scale — the same pattern applies. Pairs of (input, expert verdict) exist; what does not exist is a written-down rubric that captures the implicit consensus across the panel of experts. Distillation produces that rubric directly from the data, without forcing experts into an interview loop they are constitutionally bad at.

Two conditions limit the transfer. First, the panel needs enough independent reviewers per item that the aggregate is more than one reviewer's idiosyncrasy — without that, the LLM is distilling individual taste rather than collective methodology. Second, the inputs need to be machine-readable enough that the LLM can pull useful features from them. Pitch transcripts are; medical scans are not, at least not by the same models. Distillation is method, not magic.

### 5.3 Limitations

The transcript reduction loses information that the video does not. A founder who pauses meaningfully, who shows a working demo, who handles a hostile question with grace in the live setting communicates things the transcript flattens. The system as described filters on transcripts because that is what scales; a system that filters on audio or video would be a richer system, and the transferable lessons may not hold. Earlier work in this direction is sparse and rapidly evolving.

The N = 35 sample is the most-stated limitation and the one most worth taking seriously. It is large enough to demonstrate the alignment is real and to support specific claims about which prompting strategies work, but it is not large enough to support claims about how the methodology generalizes across sectors or across time. The natural follow-up paper is a larger replication on the Cyrannus production data, which is anonymized in [`code/data/ai_reviews_prod_anon.csv`](../code/data/ai_reviews_prod_anon.csv) (109 startups; less expert-labelled but useful as an out-of-sample check).

The model providers will change. The specific configurations reported in Table 1 reflect the Claude and GPT-4 versions available at the time of the experiments; either provider's next release may shift the numbers up or down. The prompting strategies should remain comparable in their relative ordering, since the structural properties (decomposition, chain-of-thought, methodology presence) are not provider-specific. But the absolute numbers will move.

The model does not see, and cannot reason about, the things experts learn from years of dealing with founders directly. It does not know that this team's prior employer has a reputation for producing specific kinds of competence. It does not know that a particular vertical has been recently re-examined by tier-1 funds and the consensus has shifted. That knowledge is what the human reviewer brings, and the system is designed around the assumption that they bring it. Removing the human is not the goal.

### 5.4 The Gaming Risk

Any deployed evaluation system faces the question of whether the entities being evaluated will adapt to the evaluator. If founders learn the LLM weights specific TAM citations, named team credentials, and quantified traction, they will start including those things — which is what the system is designed to encourage. The risk is that founders learn to *fake* those things, and the LLM, lacking the means to verify the underlying claims, accepts the fakery as substance.

The mitigation is architectural rather than technical. The LLM is the first stage; the human expert is the second stage. A founder who fakes a TAM number gets through the LLM filter and lands in front of a human reviewer who knows the sector and will catch the fake. A founder who fakes named team credentials encounters the same human reviewer. The two-stage architecture does not require the LLM to be unfoolable; it requires the LLM to be unfoolable *in ways the human is also unfoolable*. The combined system is stronger than either alone, which is the architectural property Paper 1 calls multi-stage complementarity.

The longer-term mitigation is that the criteria evolve. If a particular pattern of LLM-friendly fakery emerges in the data, the methodology distillation can be re-run with explicit attention to that pattern, and the prompts updated. This is the same arms-race dynamic that any signal-detection system faces and is well-understood in adjacent domains (search ranking, content moderation, fraud detection). The architecture supports it.

---

## 6. Conclusion

The expert-time bottleneck at the screening stage of early-stage venture capital is not a problem of expert availability. It is a problem of expert *allocation*. The current architecture spends most of the available expert attention on extracting basic content from variable-quality presentation, and very little on evaluating the substantive question of whether the business will work. An LLM, prompted with a methodology distilled from the expert panel itself, can do most of the content-extraction work at NDCG@20 = 0.923 alignment with a ten-expert aggregate, leaving the experts to spend their time on the part of the evaluation where their judgment is irreplaceable.

The methodological contribution — instruction distillation — is the move that makes this work. It avoids the failure mode of asking experts to articulate a rubric they cannot articulate, and instead extracts the rubric from the data the panel has already produced. This generalizes beyond pitch ranking; anywhere a panel produces aggregate judgments without a unified written rubric, the same approach should apply.

The architectural contribution is that the LLM is positioned as a first-stage filter, not as a replacement for human judgment. The combined two-stage architecture is the operational instantiation of the platform-architecture concept in Paper 2, and the empirical NDCG numbers in this paper are what feed back into Paper 2's sensitivity analysis as the realistic σ_AI anchor.

The smaller, harder honesty is this: a paper about replacing biased human judgment was itself produced through a process — peer review, editorial selection, citation politics — that the LENS framework predicts is subject to exactly the dynamics it describes. The framework does not exempt its authors. The platform that deploys these results is staffed by people who, like everyone else, evaluate pitches under the same cognitive constraints the paper documents. We are not standing outside the system we are describing. The methodology described above is one mitigation, not a solution; the solution, if there is one, is iterative and architectural and nobody owns it.

---

## Reproducibility

Every NDCG number in this paper is reproduced exactly by [`code/paper3_llm_eval/aggregate_ndcg.py`](../code/paper3_llm_eval/aggregate_ndcg.py) reading [`code/data/ai_reviews_research_anon.csv`](../code/data/ai_reviews_research_anon.csv). The four prompt files are at [`code/paper3_llm_eval/prompts/`](../code/paper3_llm_eval/prompts/) and the orchestrator that re-runs the experiments end-to-end (given API keys for both providers) is [`code/paper3_llm_eval/run_experiments.py`](../code/paper3_llm_eval/run_experiments.py). The reference implementation of the per-criterion evaluation pipeline is [`code/paper3_llm_eval/pitch_evaluator.py`](../code/paper3_llm_eval/pitch_evaluator.py). The full experimental setup is reproducible with the data as released; the underlying confidential transcripts and startup identities are not.

---

## References

Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? In *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency* (pp. 610–623). ACM.

Bernstein, S., Korteweg, A., & Laws, K. (2017). Attracting early-stage investors: Evidence from a randomized field experiment. *The Journal of Finance*, 72(2), 509–538.

Brooks, A. W., Huang, L., Kearney, S. W., & Murray, F. E. (2014). Investors prefer entrepreneurial ventures pitched by attractive men. *Proceedings of the National Academy of Sciences*, 111(12), 4427–4431.

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., … Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems*, 33, 1877–1901.

Chiang, C.-W., & Yin, M. (2021). You'd better stop! Understanding human reliance on machine learning models under covariate shift. In *Proceedings of the 13th ACM Web Science Conference* (pp. 120–129). ACM.

Clark, C. (2008). The impact of entrepreneurs' oral "pitch" presentation skills on business angels' initial screening investment decisions. *Venture Capital*, 10(3), 257–279.

Cumming, D., & Groh, A. (2018). The impact of entrepreneurial finance on start-up activity. *Journal of Banking & Finance*, 100, 253–269.

Davenport, T., & Ronanki, R. (2018). Artificial intelligence for the real world. *Harvard Business Review*, 96(1), 108–116.

Deloitte Insights. (2021). *Making the investment decision process more naturally intelligent.*

Hochberg, Y. V., Ljungqvist, A., & Lu, Y. (2007). Whom you know matters: Venture capital networks and investment performance. *The Journal of Finance*, 62(1), 251–301.

Kamps, H. J. (2023). This AI will tell you if your pitch deck is good enough. *Medium*, 27 October.

Maarouf, A., Feuerriegel, S., & Pröllochs, N. (2024). A fused large language model for predicting startup success. arXiv:2409.03668.

OpenAI. (2023). *GPT-4 Technical Report.* arXiv:2303.08774.

Pollack, J. M., Rutherford, M. W., & Nagy, B. G. (2012). Preparedness and cognitive legitimacy as antecedents to new venture funding in televised business pitches. *Entrepreneurship Theory and Practice*, 36(5), 915–939.

Serrano, C. J. (2010). The dynamics of the transfer and renewal of patents. *RAND Journal of Economics*, 41(4), 686–708.

Tam, K. Y., & Kiang, M. Y. (2012). Managerial applications of text mining. *ACM Transactions on Management Information Systems*, 3(1).

Yankov, B., Ruskov, P., & Haralampiev, K. (2014). Models and tools for technology start-up companies success analysis. *Economic Alternatives*, 3, 15–24.
