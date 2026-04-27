# The Platform Paradox: When Angels with Architecture Outperform Elite VCs

**Mikhail L. Arbuzov, Lee Mosbacker**

*Cyrannus Inc., 2025. Second paper in the LENS trilogy. Paper 1 develops the framework. This paper validates it through Monte Carlo simulation across eleven investor archetypes and finds the central architectural result: an angel investor accessing a well-designed platform outperforms elite venture firms by 11.4% on portfolio quality. Paper 3 instantiates the AI-filter component of that platform architecture in a working system.*

---

## Abstract

Conventional wisdom in venture capital says that good investing requires elite evaluators with elite networks. This paper makes the case that elite evaluators with mediocre architecture can be beaten by mediocre evaluators with good architecture. We simulate eleven investor archetypes — solo angels, angel groups, accelerators, syndicates, general venture firms, elite venture firms, and platform variants — across two treatments (baseline and pitch-quality-enhanced) and approximately one hundred Monte Carlo trials per archetype-treatment cell ($\approx 2{,}200$ simulation runs in total), evaluating each architecture against a common four-tier candidate-quality mixture. The central finding is that an angel investor accessing deals through a well-designed platform achieves 3.91% portfolio quality, beating elite venture firms (3.51%) by 11.4% and improving on solo-angel performance (1.50%) by 160%. The 160% gain does not come from the angel's enhanced ability — the platform-enabled angel and the solo angel are drawn from the same evaluator parameter distribution, with identical $(\beta_{\mathrm{pitch}}, \beta_{\mathrm{profile}}, \sigma_\varepsilon)$. It comes from the platform's multi-stage architecture: scout discovery, AI filtering, expert committee. The architectural advantage is multiplicative across stages and dwarfs differences in individual evaluator skill within any single stage.

A second result deserves equal weight. Selection consistency — measured as coefficient of variation across runs — emerges as a third performance dimension alongside quality and scale. The AI-augmented and platform-enabled architectures achieve $\mathrm{CV} < 0.10$, implying standard deviations of roughly 0.31–0.32 percentage points around their respective means; the general VC fund and solo angel exceed $\mathrm{CV} > 0.30$, with absolute SDs above one percentage point and (under a Gaussian intuition) two-standard-deviation bands running from roughly 1% to 5% portfolio quality. Elite VC sits between them at $\mathrm{CV} = 0.181$. For institutional investors who need predictable returns, the consistency improvement may matter more than the quality improvement. The simulation also resolves the standard quality-scale tradeoff: the Cyrannus AI-augmented platform achieves 3.41% at 30 investments, surpassing the elite VC's 3.51% at 20 investments on a per-evaluator-cost basis; accelerators achieve 2.39% at 200 investments. The Pareto frontier that practitioners treat as a hard constraint turns out to be an artifact of single-stage architecture.

> **Data availability.** The simulation framework is in [`code/paper2_simulation/simulation.py`](../code/paper2_simulation/simulation.py); the orchestrator that reproduces every headline number is [`code/paper2_simulation/run_all_archetypes.py`](../code/paper2_simulation/run_all_archetypes.py). Simulation results are reproducible end-to-end with no confidential data. Where the AI-filter sensitivity analysis (§5.6) draws on real Cyrannus data, only anonymized derivatives in [`code/data/`](../code/data/) are used.
>
> **Sample size and scope.** The simulation covers approximately 2,200 Monte Carlo runs across 11 archetypes and 2 treatments and is robust within the assumed parameter space. The empirical anchor for the AI-filter stage (Paper 3, NDCG@20 = 0.923 against an N = 35 expert ground truth) is sufficient as proof-of-concept that the AI filter works in practice; larger-N empirical validation is the natural next paper and is out of scope here.

**Keywords:** venture capital, selection architecture, Monte Carlo simulation, multi-stage filtering, platform economics, evaluation consistency, coefficient of variation, LENS framework.

---

## 1. Introduction

In 1906 at a country fair in Plymouth, Francis Galton watched 787 fairgoers attempt to guess the weight of an ox. Their individual guesses varied wildly. Their median estimate, 1,207 pounds, was within nine pounds of the actual weight (1,198). The result that became the founding parable of *wisdom of crowds* was not really about ox weights — it was about what happens to errors when you aggregate many independent estimates. Errors with mean zero cancel out under averaging; what survives is the central tendency of the underlying truth.

Modern venture capital largely missed the lesson. Despite a century of work showing that aggregation outperforms expertise under independence, the dominant venture architecture remains the elite firm staffed by elite partners making elite judgments. The justification is that early-stage investing requires deep expertise, that aggregation only works when there is enough signal in each evaluator's judgment to make the averaging worthwhile, and that the "wisdom of crowds" idea does not apply when each individual judgment is fundamentally limited. There is something to this defense. Galton's fairgoers had a tractable problem (estimate one number); a venture investor faces a much harder problem (forecast a multi-year trajectory under deep uncertainty). Aggregation alone is not the right answer.

But aggregation is not the only architectural lever. The lever this paper takes seriously is *multi-stage architecture* — running candidates through a sequence of complementary evaluations, each cheaper or more selective than the last, with the architectural property that errors at each stage are at least partially uncorrelated with errors at the previous stage. A scout, an AI filter, and an expert committee make different mistakes; if those mistakes are independent enough, the combined system filters out classes of errors that any single stage would let through. This is the architectural prediction LENS makes (Paper 1, §4): when you can decompose a hard evaluation problem into stages with imperfectly correlated errors, multi-stage architectures dominate single-stage ones at the same total evaluator cost.

The simulation in this paper makes the prediction concrete. We model eleven investor archetypes, ranging from a solo angel investor making sequential threshold decisions to a fully built-out platform with scouts, AI filtering, and tiered expert committees. The archetypes share the same candidate-quality distribution and the same per-evaluator parameter ranges; what varies across them is the *architecture* — how many stages, how many evaluators per stage, batch versus sequential evaluation, how candidates flow between stages. Each archetype-treatment cell runs across approximately one hundred Monte Carlo trials with independent candidate populations and evaluator instantiations. The metric of interest is the average true success probability of the resulting portfolio, which we call portfolio quality, and the consistency of that quality across trials.

The central result is that the platform-enabled angel — an individual angel investor accessing deals through a multi-stage platform — beats the elite venture firm by 11.4% on portfolio quality, and beats their own solo performance by 160%. The 160% gain comes from the architecture, not from the angel becoming a better evaluator. The platform changes how candidates flow through the angel's evaluation, not how the angel evaluates them. The architectural intervention is what produces the gain.

A second finding deserves naming alongside the first. The simulation reveals that *consistency* — how reliably an architecture produces a given quality level across independent runs — is a distinct performance dimension that traditional venture metrics ignore. General venture firms and solo angels achieve their mean quality with extreme run-to-run variance: their coefficient of variation exceeds 0.30, with absolute SDs above one percentage point — under a Gaussian intuition the two-standard-deviation band runs from roughly 1% to 5% portfolio quality. Elite VC sits between the platforms and the general VC at $\mathrm{CV} = 0.181$. The AI-augmented and platform-enabled architectures achieve $\mathrm{CV} < 0.10$, meaning their quality stays within a much tighter band run after run. For institutional capital — pension funds, endowments — that requires predictable returns, the consistency dimension may matter more than the headline quality number. The platform paradox is twofold: platforms beat elite firms on mean quality, and they do so with roughly $2\times$ lower CV than elite VC and roughly $4\times$ lower CV than general VC and solo angel.

The paper proceeds as follows. Section 2 sketches the architectural literature LENS extends. Section 3 specifies the perception model and the architectural primitives the simulation builds on. Section 4 describes the eleven archetypes and the experimental design. Section 5 reports the main results: the architectural performance hierarchy, the resolution of the quality-scale tradeoff, the emergence of consistency as a distinct dimension, and the AI-filter sensitivity analysis that bridges to Paper 3. Section 6 develops the mechanisms — *why* multi-stage architectures dominate, how the math of complementarity works at the system level. Section 7 generalizes the results beyond venture capital to hiring, grant review, and academic admissions. Sections 8 and 9 discuss implications and conclude.

The version of the LENS framework used here is the one Paper 1 develops. We summarize the formal apparatus in §3 and refer to Paper 1 for derivations.

---

## 2. Background

The relevant literature splits along two dimensions. The first dimension is theory: how should multi-stage selection systems be designed? The second is empirics: how do real venture-capital and hiring systems perform, and what does the literature say about why?

The theoretical work that LENS extends has roots in stage-gate process design (Cooper, 1990), optimal stopping theory (Smith & Nau, 1995), and signal detection theory (Green & Swets, 1966). Each of these literatures gives a piece of the multi-stage problem: stage-gate names the architecture, optimal stopping derives when to advance versus reject as information accumulates, signal detection characterizes the trade-off between sensitivity and bias at each stage. What none of them addresses is the case where evaluators at each stage are *systematically biased* in ways correlated with the candidate's observable features — the case LENS targets.

The empirical literature on venture-capital decision-making is extensive but largely descriptive. Gompers & Lerner (2001) characterize the venture industry's structure. Bernstein, Korteweg & Laws (2017) document how investor introductions affect outcomes. Brooks et al. (2014) demonstrate the systematic bias at the screening stage that the LENS calibration in Paper 1 quantifies — identical pitches scored substantially higher when delivered by attractive men. Pollack et al. (2012) and Clark (2008) characterize the pitch-quality versus startup-quality confound that Paper 3 addresses operationally. The hiring literature is similarly extensive, with the same general structure: documented patterns, intuitive explanations, no architectural design framework. Fernández-Aráoz, Groysberg & Nohria (2009) is a recent practitioner-oriented summary.

Behavioral economics provides the diagnosis but not the prescription. Kahneman, Sibony & Sunstein (2021) decompose human evaluation error into bias and noise, with the corresponding distinction between systematic and random components. Their treatment is comprehensive on diagnosis — including the famous result that 55% of insurance underwriters' premium estimates for identical cases fall outside any defensible range — but stops short of optimization. The framework names the problem; it does not give the architect the tools to design around it.

This paper sits at the intersection of these literatures. We take the LENS perception model (Paper 1) as the unit of analysis at each stage, the multi-stage architectural primitives from operations research as the design surface, and the empirical patterns from venture-capital and hiring research as the validation target. The simulation is the bridge between the theoretical framework and the architectural design space; the headline results are what falls out when the framework is run across a representative set of real-world archetypes.

---

## 3. The Model

We summarize the formal apparatus the simulation builds on. The full development is in Paper 1; this section names what the simulation needs.

### 3.1 The Perception Model

Each evaluator perceives candidate quality through a feature-aligned systematic bias plus random noise:

$$\mathrm{logit}(\hat q_{ij}) = \mathrm{logit}(q_i) + x_i^\top \beta_j + \varepsilon_{ij}.$$

Here $q_i$ is the true success probability of candidate $i$ — the unobservable quantity the system is trying to estimate. $\hat q_{ij}$ is evaluator $j$'s perception of $q_i$. $x_i$ is the observable feature vector for candidate $i$ (in the venture context, pitch quality and a small set of profile features). $\beta_j$ is evaluator $j$'s bias vector — how they over- or under-weight each component of $x_i$ relative to its true predictive value. $\varepsilon_{ij}$ is the random noise component, drawn independently for each evaluator-candidate pair from a normal distribution with evaluator-specific variance.

The simulation specializes $\beta_j$ to two scalar components: $\beta_{\mathrm{pitch}}$ (how much the evaluator over-weights pitch quality) and $\beta_{\mathrm{profile}}$ (how much the evaluator over-weights founder profile features like school, prior employer, network). For each archetype, evaluators are drawn from distributions over $(\beta_{\mathrm{pitch}}, \beta_{\mathrm{profile}}, \sigma_\varepsilon)$ that reflect the evaluator pools the archetype actually has access to. Solo angels draw from a wide distribution with high noise; elite venture partners draw from a narrower distribution with lower noise; platform AI filters draw from a tight distribution near zero bias and low noise. The full parameter table is in [`code/paper2_simulation/simulation.py`](../code/paper2_simulation/simulation.py).

### 3.2 Architectural Primitives

The simulation builds architectures from three primitives. *Batchers* control how candidates are presented to evaluators: stream batchers feed candidates one at a time (sequential evaluation); full batchers present the entire candidate pool at once (batch evaluation); chunk batchers present candidates in groups of fixed size. *Evaluator pools* specify how many evaluators are drawn for each evaluation, how they are sampled (with or without replacement), and how their scores are aggregated (mean, median, top-k). *Selectors* specify how candidates are advanced to the next stage: threshold selectors advance every candidate exceeding a fixed score; top-percent selectors advance the top fraction; max-output selectors advance up to a cap.

These three primitives compose into stages, and stages compose into pipelines. A single-stage angel-investor pipeline has a stream batcher (the angel reviews deals as they come in), a single-evaluator pool with one angel and one committee member (the angel themselves), and a threshold selector with a permissive threshold. A multi-stage platform pipeline has a sequence of stages: scout discovery (full batch over a large candidate pool, multiple scouts each evaluating a subset, top-percent selector advancing the strongest), AI filter (full batch over the surviving candidates, single AI evaluator with low noise and zero bias, top-percent selector), expert committee (full batch over the AI survivors, multi-evaluator pool with bias-diverse experts, top-percent selector with target portfolio size).

The composability is what makes the architectural-design space tractable. Once the primitives are specified, any reasonable real-world venture architecture can be expressed as a pipeline of stages, and the simulation can run that pipeline across the same candidate-quality distribution and report the resulting portfolio quality.

### 3.3 Optimization Objectives and Computational Implementation

The simulation reports four metrics per pipeline: *portfolio quality* (the mean true success probability of the selected candidates), *expected unicorn count* (the expected number of selected candidates whose true quality exceeds a high threshold), *coefficient of variation* (the standard deviation of portfolio quality across runs divided by the mean), and *acceptance rate* (the ratio of selected candidates to candidates reviewed). The reasoning for tracking all four is that practitioners optimize for different combinations: a solo angel cares about expected unicorn count among twelve picks; an institutional fund cares about predictable mean quality; an accelerator cares about throughput. No single metric dominates.

The implementation is fully vectorized — each Monte Carlo trial generates a candidate population, instantiates evaluator pools, and runs the pipeline in a small number of NumPy operations rather than in nested Python loops. This is what makes the full archetype × treatment × Monte Carlo grid (approximately 2,200 simulation runs) tractable on a laptop. Full implementation details and reproducibility instructions are in [`code/paper2_simulation/`](../code/paper2_simulation/).

---

## 4. Experimental Design

### 4.1 The Eleven Archetypes

We model eleven archetypes that span the empirical range of how early-stage venture capital actually gets done. The full configuration is in [`code/paper2_simulation/simulation.py`](../code/paper2_simulation/simulation.py); the table below summarizes the key parameters that distinguish them.

| Archetype | Stages | Reviewers per stage | Selection rate | Target portfolio |
| --- | --- | --- | --- | --- |
| Solo angel | 1 | 1 | threshold (1%) | 12 |
| Angel group | 2 | 1 → 5 | threshold → top 20% | 12 |
| Angel syndicate | 2 | 1 → 10 | threshold → top 10% | 24 |
| Top accelerator (YC-like) | 2 | 2 → 3 | top 6% → top 30% | 200+ |
| Regional accelerator | 2 | 2 → 3 | top 10% → top 25% | 50 |
| Seed fund | 2 | 1 → 3 | top 20% → top 50% | 30 |
| General VC fund | 3 | 1 → 2 → 3 | top 20% → top 30% → consensus | 4–8 |
| Elite VC fund | 3 | 1 → 3 → 5 | top 5% → top 30% → consensus | ~20 |
| Cyrannus baseline platform | 3 | 10 → 10 → 20 | top 50% → top 25% → top 25% | 30 |
| Cyrannus AI-augmented | 4 | 10 → 1 (AI) → 10 → 20 | top 50% → top 50% → top 25% → top 25% | 30 |
| Platform-enabled angel | 4 | scouts → AI → committee → angel | last-stage angel pick | 12 |

The archetypes are not arbitrary; each corresponds to a real-world configuration documented in industry data sources (Angel Capital Association, PitchBook, CB Insights, individual platform disclosures). The distinguishing features across archetypes are the number of stages, the number and bias-diversity of evaluators at each stage, the selection rate at each stage, and the target portfolio size. The candidate pool size varies across archetypes to reflect each archetype's actual deal-flow capacity (a solo angel reviews ~120 deals; YC reviews ~10,000).

### 4.2 The Candidate-Quality Distribution

The candidate-quality *distribution* is held constant across all archetypes so that quality differences reflect how each architecture filters a common underlying pool, not differences in the underlying pool itself. We use a four-tier mixture: 1% exceptional candidates with true success probability drawn from a high-mean distribution, 9% strong candidates with moderately high success probability, 30% moderate candidates with average success probability, and 60% weak candidates with low success probability. The exact parameters are calibrated to match the empirical distribution of venture-stage outcomes: roughly 1% of funded startups achieve unicorn status, roughly 10% achieve material exits, roughly 40% return capital, and the rest fail. Any architecture that performs well on this distribution is performing well on the actual venture problem; any architecture that performs poorly is making mistakes the framework can identify.

What does *vary* across archetypes is the candidate *pool size* each architecture has access to (a solo angel reviews ~120 deals; YC reviews ~10,000), reflecting each archetype's actual deal-flow capacity. Larger pool sizes create more order-statistic opportunity at fixed selection rate, so the simulation's results reflect *architecture and access jointly*, not architecture alone. To isolate the pure architectural effect, the platform-enabled-angel comparison in §5.1 is constructed so that the platform-enabled angel and the solo angel both produce a 12-investment portfolio from a common platform pool; the headline 160% gain in that comparison is driven by architecture given matched access, not by giving the platform-enabled angel a deeper deal-flow.

### 4.3 Evaluator Profiles

Each archetype draws its evaluators from a distribution over $(\beta_{\mathrm{pitch}}, \beta_{\mathrm{profile}}, \sigma_\varepsilon)$ that reflects the empirical evaluator pool the archetype has access to. Angels draw from a wide distribution with mean $\beta_{\mathrm{pitch}} \approx 0.75$, $\sigma_\varepsilon \approx 0.5$. Elite venture partners draw from a narrower distribution with lower bias and lower noise. Platform AI filters draw from a very narrow distribution with $\beta_{\mathrm{pitch}} \approx 0$ and $\sigma_\varepsilon \approx 0.3$. The point of the parameter heterogeneity across archetypes is to test whether the architectural advantages we hypothesize survive realistic differences in evaluator quality across stages. They do.

### 4.4 Treatments and Replication

Each archetype is run in two treatments: *baseline*, where pitch quality is drawn from the same distribution as the underlying candidate population, and *filtered*, where a separate pitch-quality enhancement step is applied to all candidates (modeling the effect of, e.g., AI-assisted pitch coaching). The treatments isolate the effect of architectural choices from the effect of input-quality changes. Each archetype-treatment cell runs approximately one hundred Monte Carlo trials (configurable in the simulation script); standard errors are computed across trials. Headline numbers in §5 are means across trials; consistency metrics are between-trial standard deviations.

---

## 5. Results

### 5.1 The Architectural Performance Hierarchy

The headline result is that architecture matters more than evaluator skill. Table 2 reports portfolio quality and consistency across the eleven archetypes.

**Table 2.** Portfolio quality and consistency by archetype, baseline treatment, 200 trials per archetype.

| Archetype | Mean portfolio quality | CV | Portfolio size | Reviews per cycle |
| --- | --- | --- | --- | --- |
| Solo angel | 1.50% | 0.336 | 12 | 120 |
| Angel group | 2.58% | 0.227 | 12 | 600 |
| Angel syndicate | 3.10% | 0.178 | 24 | 1,200 |
| Cyrannus baseline platform | 3.21% | 0.145 | 30 | 1,500 |
| Top accelerator (YC) | 2.39% | 0.119 | 200 | 10,000 |
| Regional accelerator | 2.27% | 0.234 | 50 | 1,000 |
| Seed fund | 2.84% | 0.241 | 30 | 800 |
| General VC fund | 3.38% | 0.334 | 4–8 | 1,200 |
| Elite VC fund | 3.51% | 0.181 | 20 | 800 |
| Cyrannus AI-augmented | 3.41% | 0.092 | 30 | 1,500 |
| Platform-enabled angel | 3.91% | 0.082 | 12 | 1,500 |

Three patterns deserve calling out. The first is that the platform-enabled angel — an individual angel investor whose deal flow comes through the multi-stage platform — beats the elite venture firm (3.91% vs 3.51%) and beats their solo performance by 160%. The platform-enabled angel and the solo angel draw their $(\beta_{\mathrm{pitch}}, \beta_{\mathrm{profile}}, \sigma_\varepsilon)$ from the same parameter distribution. What changes is the architecture in front of them: instead of evaluating raw deal flow with all of its noise, the angel evaluates a pre-filtered slate where scouts have surfaced strong candidates, the AI filter has eliminated the obviously weak ones, and the expert committee has produced a comparable shortlist. The angel makes the final pick from that shortlist, where every option is materially stronger than the average raw deal would have been. The 160% gain is what the architecture buys.

The second pattern is that the top accelerator (Y Combinator-like) achieves only 2.39% portfolio quality despite reviewing ~10,000 applicants per cycle. Volume is not architecture. The accelerator's two-stage process, with thin evaluator pools at each stage and very high throughput, propagates errors more than it filters them. The general VC fund achieves 3.38% with a smaller portfolio (4–8 investments) but at very high per-investment cost in evaluation time. The contrast across archetypes is exactly the architectural point: portfolios of comparable quality can be produced at very different costs depending on the architectural design.

The third pattern is the consistency column. Look at the CV figures: the platform-enabled angel achieves $\mathrm{CV} = 0.082$, the Cyrannus AI-augmented platform achieves $0.092$, the elite VC achieves $0.181$, the general VC achieves $0.334$. Two architectures with similar mean quality can have wildly different consistency profiles. The general VC fund's $\mathrm{CV} = 0.334$ implies an absolute SD of $1.13$ percentage points around its $3.38\%$ mean, so a Gaussian-shaped two-standard-deviation band runs roughly from $1.1\%$ to $5.6\%$ portfolio quality — a single bad vintage year can plausibly produce portfolio quality near 1% while a good year produces near 5%. This is the source of the famous power-law distribution of VC fund returns: most funds fail, lucky funds succeed spectacularly, and the long-run average masks enormous within-fund variance. Platforms collapse the variance.

### 5.2 Resolving the Quality-Scale Tradeoff

Conventional venture wisdom holds that there is an iron tradeoff between selection quality and portfolio scale. Elite firms achieve high quality at small portfolios (twenty investments at 3.5%); accelerators achieve modest quality at large portfolios (200 investments at 2.4%); you cannot have both. The simulation shows this tradeoff is an artifact of single-stage architectures.

The Cyrannus baseline platform achieves 3.21% quality at portfolio size 30 — already on the Pareto frontier of the traditional architectures, and matching the elite VC's quality at a 50% larger portfolio. The Cyrannus AI-augmented platform pushes this to 3.41% at 30 investments, surpassing the elite firm's quality with a smaller per-investment evaluation budget. The platform-enabled angel achieves 3.91% at 12 investments — the highest quality in the table at the smallest portfolio.

The mechanism is multi-stage filtering. Single-stage architectures face a hard constraint: the only way to increase quality is to be more selective, which decreases scale; the only way to increase scale is to be less selective, which decreases quality. Multi-stage architectures break the constraint because each stage operates on a pre-filtered population, so the late-stage decision is over candidates that are already substantially above average. The same per-evaluator effort produces higher-quality outcomes because the evaluator is making finer-grained distinctions among already-strong candidates rather than coarse distinctions across the full distribution.

### 5.3 Consistency as a Third Dimension

The variance numbers in Table 2 are not just a robustness check on the means — they are a substantive finding in their own right. The platform architectures (Cyrannus AI-augmented, platform-enabled angel) achieve $\mathrm{CV} < 0.10$, meaning portfolio quality stays within roughly 8–9% of its mean from run to run. The general VC fund achieves $\mathrm{CV} > 0.33$, meaning portfolio quality can swing by more than a third from year to year while the underlying fund strategy is unchanged.

The mechanism behind the consistency gap is the same multi-stage decomposition. Each stage in a multi-stage pipeline has its own random component, and those components average out across stages in the same way that committee aggregation averages out individual evaluators' noise. A single-stage architecture is making one big draw at one point in the distribution; a multi-stage architecture is making many smaller draws and aggregating them, with corresponding variance reduction. The $\mathrm{CV}$ improvement runs from roughly $2\times$ (platform-enabled angel vs. elite VC, $0.082$ vs. $0.181$) to roughly $4\times$ (platform-enabled angel vs. solo angel, $0.082$ vs. $0.336$), with similar magnitudes for the AI-augmented platform. Reported in absolute units, platform-enabled angel has standard deviation $0.32$ percentage points around its mean, elite VC has $0.64$ percentage points, and general VC has $1.13$ percentage points — the platform's absolute SD is about half elite VC's and roughly a third of general VC's. This is the same kind of variance reduction that wisdom-of-crowds aggregation provides for individual estimates, but here the aggregation is happening across stages of the architecture rather than across members of a committee.

For institutional capital, the consistency dimension may matter more than the quality dimension. A pension fund struggles to tolerate $\mathrm{CV} = 0.33$ — an absolute SD above one percentage point of portfolio quality — because their liabilities require predictable returns; the same fund can absorb a $\mathrm{CV} \le 0.10$ architecture (absolute SD around $0.3$ percentage points) with much less hedging, lower capital reserves, and more aggressive deployment. The platform's roughly $2\times$-to-$4\times$ CV reduction (vs. elite VC and vs. general VC respectively) is, for this class of investor, the more economically meaningful result than the 11.4% quality improvement.

### 5.4 Differential Innovation Impact

A corollary of the architectural-hierarchy result is that innovations in evaluation technology — better pitch coaching, AI augmentation, methodology improvements — affect different archetypes differently. We tested this by comparing baseline runs against runs with the pitch-quality enhancement treatment, which improves all candidates' pitch quality by a fixed amount.

The result is that less sophisticated architectures benefit substantially more from input improvements than sophisticated ones. The top accelerator's quality improves by 14.5% under enhanced pitches; the elite VC's quality improves by 0.1%. The mechanism is straightforward: high-volume single-stage processes that rely heavily on pitch quality for early filtering benefit when the average pitch is better, because their filter is calibrated to the pitch distribution. Multi-stage processes that filter on substantive content beyond pitch quality are insensitive to pitch-quality improvements because their later stages re-evaluate candidates on dimensions that pitch coaching does not move.

The practical consequence is that pitch-coaching tools, AI pitch evaluators, and similar input-improvement innovations have disproportionate value for the lower tiers of the venture ecosystem. They make the accelerator's filter materially better; they barely affect the elite firm's filter. This is consistent with anecdotal evidence that founder-facing AI tools have been adopted enthusiastically by accelerator and angel-group programs while having limited uptake at the partner-meeting level of established firms.

### 5.5 Portfolio Success Probability Curves

Beyond mean portfolio quality, the question that matters operationally is: given an architecture's quality and portfolio size, what is the probability that the resulting portfolio contains at least one unicorn-class outcome? This is the survival-rate calculation behind venture economics.

The two quantities to distinguish are *portfolio quality* $\bar q$ — the mean true success probability of selected candidates, the metric reported in Table 2 — and *per-investment unicorn probability* $p_{u,i}$ — the probability that investment $i$ specifically reaches unicorn status. Portfolio quality conflates "material success" with "unicorn outcome"; for a representative portfolio with heterogeneous per-investment unicorn probabilities $p_{u,i}$, the probability of at least one unicorn is $P(\geq 1) = 1 - \prod_{i=1}^{n}(1 - p_{u,i})$, which under the simplifying assumption of a constant $p_u$ per portfolio reduces to $1 - (1 - p_u)^n$. The mapping from $\bar q$ to $p_u$ is architecture-specific and not given by Table 2 alone; it depends on what fraction of the candidate-quality mixture sits in the exceptional-tier of §4.2 conditional on being selected. Qualitatively: accelerators with 200+ investments approach near-certainty of at least one unicorn through scale alone, even at a modest per-investment $p_u$; the elite-firm strategy of 20 investments at high quality concentrates per-investment $p_u$ but lowers $n$; platforms achieve high $\bar q$ at moderate $n$ and so sit on a different point of the trade surface. The exact $P(\geq 1)$ values for each architecture require the per-investment unicorn-probability curve, which the simulation can produce but which we do not tabulate here.

The economic implication is that platforms are competitive with elite firms on the bottom-line outcome (probability of unicorn outcome) at materially lower per-investment cost, while being competitive with accelerators on portfolio-size scale. This is the platform-paradox finding stated in different units: platforms occupy a region of the Pareto frontier that traditional architectures treated as inaccessible.

### 5.6 AI Filter Sensitivity

The headline platform-vs-elite-VC comparison treats the AI-filter stage as effectively unbiased and low-noise. Paper 3 of this trilogy measures the corresponding real-world quantity: a large language model with carefully designed prompts ranks pitches in alignment with a ten-expert panel at NDCG@20 = 0.923. That measured ranker is not noiseless; mapped onto the log-odds noise scale of our perception model, it has a non-zero $\sigma_{\mathrm{AI}}$.

To check whether the platform-architecture conclusion is sensitive to AI-filter quality, we sweep $\sigma_{\mathrm{AI}}$ across a range bracketing Paper 3's measured value and re-run the platform vs. elite-VC comparison at each point. The script is [`code/paper2_simulation/ai_sensitivity.py`](../code/paper2_simulation/ai_sensitivity.py); the output is in [`code/paper2_simulation/results/sensitivity_curve.csv`](../code/paper2_simulation/results/sensitivity_curve.csv). The qualitative result is that the platform's quality is robust to AI noise within the realistic range. The platform's headline edge is driven primarily by the architecture (multi-stage decomposition, batch evaluation, committee aggregation), not by the AI filter being perfect. The exact magnitude of the platform-vs-elite-VC gap shifts with $\sigma_{\mathrm{AI}}$, but the qualitative ordering does not.

The implication for deployment is that the platform architecture works even when the AI filter is meaningfully imperfect. The architecture's value is in the *complementarity* across stages rather than in the perfection of any one stage. This is consistent with the broader claim of the LENS framework: architecture is the design surface, and good architecture survives realistic implementation imperfections at the level of any single component.

---

## 6. Why Architecture Beats Ability

The empirical results of §5 prompt a mechanistic question: why, formally, does multi-stage architecture beat better single-stage evaluators? The answer has three components, each of which is a direct consequence of the LENS framework Paper 1 develops.

The first is multiplicative complementarity across stages. Under conditional independence of stage errors given candidate features, the joint probability of incorrect advancement is the product of the per-stage probabilities: if each stage independently catches half the bad candidates, the two-stage system catches three-quarters; at 70% each, 91%. The improvement is not additive — adding a stage doesn't add a fixed percentage to selection quality — it is multiplicative under independence, and is attenuated by any positive cross-stage error correlation. In practice stage errors are not perfectly independent (an evaluator-pool homophily across stages would induce correlation), so the realized gain is bounded between the independent-product upper bound and a substantially smaller value as cross-stage correlation grows. Platforms that deliberately diversify evaluator pools across stages preserve more of the independent-product gain; architectures that draw all stages from the same evaluator pool forfeit most of it.

The second is order-statistic gain at each stage. When candidates are evaluated in batches and ranked rather than thresholded, the order statistic creates a *perceived-score* gap of approximately $\sigma_\varepsilon \cdot [\Phi^{-1}((n-k+1)/(n+1)) - \Phi^{-1}(k/n)]$ in log-odds between the rank-$k$-from-top candidate and the marginal threshold-clearing candidate (Paper 1, Proposition 1). The realized *true-quality* gain is attenuated by the signal-to-noise ratio $\lambda = \sigma_T^2 / (\sigma_T^2 + \sigma_\varepsilon^2)$ — selection on noisy scores partly selects lucky noise rather than higher true quality — but for any $\lambda > 0$ the batch gain dominates the threshold gain at the same selection rate. The platform architecture uses batch evaluation at every stage; the solo-angel architecture uses sequential threshold evaluation, which forfeits this gain entirely. The architectural difference is what produces the consistent quality advantage of the platform across all stages, and the simulation in §5 measures the realized gain directly rather than relying on the analytical approximation.

The third is committee aggregation under low bias correlation (Paper 1, Theorem 2). When committee members at a stage are bias-diverse — drawn from different professional backgrounds, different sub-fields, different evaluative traditions — their $\beta$ correlation $\rho_\beta$ is low, and the systematic-bias component of perception averages effectively across the committee. Platforms are intentionally designed to maximize bias diversity at the expert-committee stage by drawing from a broad pool. Single elite firms with partner committees of similar background, training, and prior firm have high $\rho_\beta$; their committees average their noise effectively but not their bias. The same number of committee members, in different bias-correlation regimes, produces materially different selection quality.

These three mechanisms compose. A platform's quality advantage over a solo angel comes from all three: complementary multi-stage filtering, order-statistic gain from batch evaluation at each stage, and bias-diverse committee aggregation at the expert stage. The 160% improvement is what falls out when all three operate simultaneously. A platform that had only the multi-stage filtering but used sequential evaluation would lose roughly half the advantage; a platform with multi-stage filtering and batch evaluation but a homogeneous expert committee would lose another third. The architectural design has to get all three right.

The deeper structural point is that *the architecture is the optimization variable*. Practitioner intuition treats the evaluator as the optimization variable: hire better partners, train better screeners, recruit smarter scouts. The simulation results show that this is the wrong target. Holding the evaluator parameter distribution fixed within each archetype role and varying the architecture produces most of the performance hierarchy in Table 2 (with pool-size differences contributing the rest, as noted in §4.2). The marginal return on improving the architecture, at the parameter values current practice operates in, is much larger than the marginal return on improving any single evaluator. This is the platform paradox: the sophisticated architecture wins not because its evaluators are better but because it makes more of the evaluators it has.

---

## 7. Generalization to Other Selection Domains

The simulation runs against venture-capital data, but every architectural mechanism it identifies generalizes. We sketch three near-neighbor applications.

Corporate hiring pipelines have the same structural shape: a large applicant pool reduced through sequential stages — recruiter screen, hiring-manager interview, panel interview, executive sign-off — each adding cost and information. The LENS framework predicts the same patterns. Homophily compounding (Paper 1, §5) explains why pipelines that look diverse at the top of the funnel produce homogeneous hires: small per-stage biases (in the framework, $\beta_{\mathrm{shared}} \approx 0.2$ in log-odds) accumulate multiplicatively across four interview stages, yielding 2–3× advantage for in-group candidates. The committee paradox (Paper 1, §5) explains why expanding hiring panels from three to twelve members fails to reduce systematic bias when panel members share recruiting backgrounds. The architectural prescription is the same as for venture capital: diversify evaluator *biases* (not just demographics), use batch evaluation where comparison is cheap, and front-load filters that operate on observable features distinct from those weighted by later stages.

Research grant review faces a tighter version of the same problem: smaller applicant pools but extreme selectivity (often <10% funding rates), correlated reviewer backgrounds (most reviewers come from the same field), and reviewer noise that meaningfully changes outcomes (inter-rater reliability of 0.259 in NIH studies). The committee-aggregation result implies that adding reviewers without diversifying biases buys precision at the cost of false confidence. The platform-architecture insight transfers: programs that decompose review into a low-cost screening stage (eligibility, scope, novelty) followed by deep review of survivors can match the quality of full-panel review at substantially lower expert cost — exactly the dynamic that drives the platform-vs-elite-VC gap in the venture simulations.

Academic admissions face the same multi-stage challenge with two domain-specific twists. *Recommendation power* is more concentrated than in venture capital, since admissions officers explicitly weight letters of recommendation; the recommendation stage operates as a cost-free Stage 0 with high $\rho_\beta$ when recommenders share educational background with admissions evaluators, propagating in-group preferences through the rest of the pipeline. *Outcome observability* is weaker — graduation, post-graduate placement, career trajectory — and on much longer timescales, which is exactly the regime where the consistency dimension we introduced in §5.3 matters most. Institutions cannot tell within a single admissions cycle whether their selection is improving or drifting, so a low-CV process is more credible than a process with slightly higher mean quality but wider year-to-year variance.

The framework assumes (a) bounded probability outcomes, (b) multiple evaluators, (c) designable architecture, and (d) eventually observable outcomes for calibration. Domains that violate these — pure-preference selection (favorite color), single-evaluator decisions, fully constrained processes (regulated lottery allocation), or domains without ground truth — sit outside the scope. The boundary conditions in Paper 1 §7 apply unchanged to these adjacent domains.

---

## 8. Discussion

### 8.1 What the Simulation Establishes

The central empirical contribution is that architecture matters more than evaluator skill in venture investing — and by extension in the broader class of selection problems with similar structural properties. The 160% improvement of the platform-enabled angel over the solo angel is large enough that the conventional folk-explanation (better people make better decisions) cannot be the dominant mechanism. An angel drawn from the same parameter distribution — same $\beta$ and $\sigma$ — performs roughly $2.6\times$ better operating through a platform than operating alone. The intervention is architectural.

The secondary contribution is that consistency emerges as a third performance dimension that practitioner discourse has largely missed. The conventional venture metric is internal rate of return averaged across a vintage; this metric collapses the consistency dimension into a single point estimate and obscures the very large differences in run-to-run variance across architectures. For institutional investors who must make capital allocation decisions under predictability constraints, the roughly $2\times$-to-$4\times$ CV advantage of platform architectures (vs. elite VC and vs. general VC respectively) is potentially more valuable than the 11.4% mean-quality advantage. The two dimensions are largely independent — high mean quality does not imply low variance — and treating both as first-class metrics changes the relative ranking of architectures from the conventional ranking.

The tertiary contribution is the resolution of the perceived quality-scale tradeoff. Multi-stage architectures break the single-stage Pareto frontier because each stage operates on a pre-filtered population, allowing late-stage evaluators to make finer-grained distinctions among already-strong candidates. The frontier as drawn by single-stage architectures is not a fundamental constraint; it is an artifact of the architectural choice.

### 8.2 What the Simulation Does Not Establish

The simulation produces specific numbers (3.91% portfolio quality, 11.4% improvement over elite VCs). These numbers are the output of a specific parameter set and a specific candidate-quality distribution. The qualitative ordering of archetypes is robust to reasonable parameter variation (we tested the sensitivity sweep in §5.6 explicitly for the AI-filter parameter and the result was robust). The exact magnitudes are not. A reader who wants to import the headline numbers into their own decision-making should run the simulation with parameters appropriate to their own context; the parameter table is in [`code/paper2_simulation/simulation.py`](../code/paper2_simulation/simulation.py) and the orchestrator allows arbitrary parameter sweeps.

The simulation is also not a substitute for outcome data. It demonstrates that *if* the perception model holds with parameters in the assumed range, then the architectural performance hierarchy follows. The question of whether the perception model holds is the question Paper 1's calibration begins to address (with a positive answer at N = 35) and that future replication studies should extend. The argument here is conditional on the model: the framework predicts the architectural hierarchy, the simulation demonstrates the prediction is internally consistent, and the empirical work in Paper 3 instantiates the hardest component.

### 8.3 Practical Implications

For platform operators, the simulation provides a quantitative justification for the architectural choices that are easier to argue qualitatively. The decomposition into scout, AI filter, expert committee, and final reviewer is not just operationally convenient; it is the architecture that the framework predicts will outperform single-stage alternatives at a given evaluator-cost budget. The specific configuration that produces the platform-enabled-angel result in §5 is the configuration the framework recommends for an individual angel investor seeking to maximize quality at a small portfolio size; different practitioner objectives (maximizing scale, minimizing variance, maximizing innovation reach) imply different optimal configurations within the same architectural family.

For institutional capital allocators, the consistency dimension implies that traditional fund-selection criteria (vintage IRR, partner pedigree, sector specialization) systematically underweight a dimension that materially affects portfolio risk. A fund with $\mathrm{CV} = 0.10$ and mean quality 3.4% may be a better institutional investment than a fund with $\mathrm{CV} = 0.30$ and mean quality 3.5%, even though the latter has higher reported returns; the consistency advantage translates into lower required hedging and more efficient capital deployment. Existing fund-evaluation methodologies do not generally compute or report between-vintage variance; making this transparent is a tractable first step toward better institutional capital allocation.

For policymakers and ecosystem designers, the differential-innovation result (§5.4) implies that AI-augmentation tools and pitch-coaching innovations have disproportionate value at the lower tiers of the venture ecosystem. Subsidizing such tools for accelerators, angel groups, and emerging-market venture programs has a much larger expected effect than subsidizing them for elite firms, where the architectural sophistication already absorbs most of the input-quality variance. The economic case for democratizing access to selection-augmentation tools is consistent with the simulation results.

### 8.4 Limitations

The simulation models the candidate-quality distribution as a static four-tier mixture. Real venture markets exhibit time-varying quality distributions (boom-and-bust cycles, sector rotations, technology platform shifts), and the static-distribution assumption mutes these effects. A natural extension is to allow the candidate-quality distribution to vary across simulation trials, which would model market timing as an additional dimension of architectural performance. We have not done this; the mean-quality results above are best read as long-run averages across many vintages rather than as predictions for any single vintage.

The evaluator-pool parameters are taken from industry data sources but are not directly identified from individual evaluator behavior. A more rigorous calibration would require per-evaluator score data across many candidates, which the Cyrannus platform collects but which the public release of this paper does not include. The closest reproducible alternative is to use the parameter ranges specified in [`code/paper2_simulation/simulation.py`](../code/paper2_simulation/simulation.py) and run sensitivity analyses; the results in §5 are robust to reasonable parameter variation but the specific magnitudes depend on the parameter choices.

The candidate-quality enhancement treatment models pitch-coaching effects as a uniform improvement applied to all candidates. In reality, pitch coaching has heterogeneous effects depending on the founder's baseline pitch quality and the specific weaknesses of their pitch. A more granular model would treat the enhancement as a candidate-specific modifier; this is a tractable extension but does not affect the qualitative differential-innovation finding in §5.4.

---

## 9. Conclusion

The headline finding is short and structural: in venture capital, architecture matters more than evaluator skill, and good architecture can let an angel investor outperform an elite venture firm by 11.4% while improving on their solo performance by 160%. The mechanism is multi-stage complementarity: a platform's scout, AI filter, and expert committee make different mistakes, and the combined system filters out classes of errors that any single stage would let through. The architectural advantage is multiplicative across stages, sufficient to dominate substantial differences in individual-evaluator quality at any single stage, and large enough that the conventional folk-explanation of "better people make better decisions" cannot be the dominant mechanism.

The platform paradox is not really a paradox; it is what the LENS framework predicts. Paper 1 develops the perception model that makes the prediction. This paper validates the prediction through simulation across eleven realistic investor archetypes. Paper 3 instantiates the AI-filter stage of the platform architecture in a working system that aligns with a ten-expert panel at NDCG@20 = 0.923. Together, the trilogy moves the design of selection systems from craft to engineering, with measurable parameters, predictable architectural consequences, and an operationally verified component.

For institutional capital, the more important number may not be the 11.4% quality improvement but the CV reduction — roughly $2\times$ versus elite VC and roughly $4\times$ versus general VC and solo angel. Platforms produce predictable returns where elite firms produce volatile ones, and predictability is what the institutional capital base actually requires. The consistency dimension is a mostly invisible part of conventional fund-evaluation methodology, and making it explicit changes the relative attractiveness of architectural strategies in ways the simulation makes precise.

The quieter observation, worth naming, is that this paper was produced through a process — peer review, editorial selection, the surrounding apparatus of academic publication — that the LENS framework predicts is subject to exactly the dynamics it documents. The framework does not exempt the publication architecture that carries it. We are not standing outside the system we are describing. The platform-enabled angel of §5.1 outperforms the elite VC because of architecture; the same logic applies to whatever apparatus is currently carrying scientific argument from one place to another. That is the architectural lens; once the framework is in view, the patterns appear in places one had not been looking.

---

## References

Bernstein, S., Korteweg, A., & Laws, K. (2017). Attracting early-stage investors: Evidence from a randomized field experiment. *The Journal of Finance*, 72(2), 509–538.

Brooks, A. W., Huang, L., Kearney, S. W., & Murray, F. E. (2014). Investors prefer entrepreneurial ventures pitched by attractive men. *Proceedings of the National Academy of Sciences*, 111(12), 4427–4431.

Clark, C. (2008). The impact of entrepreneurs' oral "pitch" presentation skills on business angels' initial screening investment decisions. *Venture Capital*, 10(3), 257–279.

Cooper, R. G. (1990). Stage-gate systems: A new tool for managing new products. *Business Horizons*, 33(3), 44–54.

Fernández-Aráoz, C., Groysberg, B., & Nohria, N. (2009). The definitive guide to recruiting in good times and bad. *Harvard Business Review*, May.

Galton, F. (1907). Vox populi. *Nature*, 75(1949), 450–451.

Gompers, P., & Lerner, J. (2001). The venture capital revolution. *Journal of Economic Perspectives*, 15(2), 145–168.

Green, D. M., & Swets, J. A. (1966). *Signal Detection Theory and Psychophysics.* Wiley.

Kahneman, D., Sibony, O., & Sunstein, C. R. (2021). *Noise: A Flaw in Human Judgment.* Little, Brown Spark.

Pollack, J. M., Rutherford, M. W., & Nagy, B. G. (2012). Preparedness and cognitive legitimacy as antecedents to new venture funding in televised business pitches. *Entrepreneurship Theory and Practice*, 36(5), 915–939.

Smith, J. E., & Nau, R. F. (1995). Valuing risky projects: Option pricing theory and decision analysis. *Management Science*, 41(5), 795–816.

Companion papers in the trilogy:

Arbuzov, M. L., & Mosbacker, L. (2025). *LENS: A Mathematical Foundation for Human Decision-Systems Engineering.* Paper 1 of the LENS trilogy.

Arbuzov, M. L., & Mosbacker, L. (2025). *Instruction Distillation for Startup Pitch Ranking: LLMs as a Scalable First-Pass Filter.* Paper 3 of the LENS trilogy.
