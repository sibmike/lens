# LENS: A Mathematical Foundation for Human Decision-Systems Engineering

**Mikhail L. Arbuzov, Lee Mosbacker**

*Cyrannus Inc., 2025. First paper in the LENS trilogy. This paper develops the framework. Paper 2 validates it through Monte Carlo simulation across eleven investor archetypes. Paper 3 instantiates its AI-filter component in a working system that ranks startup pitches in alignment with a ten-expert crowd at NDCG@20 = 0.923.*

---

## Abstract

Practitioners across selection-heavy domains see the same patterns repeatedly. The startup that wins the competitive bidding round tends to be the one whose investor most overestimated. Hiring committees that grew from three members to twelve do not become less biased — only more confident. Recommendations get response rates an order of magnitude higher than cold introductions. Contrarian portfolios outperform consensus picks. Each of these is treated in the practitioner literature as its own phenomenon with its own folk explanation. They are not separate phenomena.

This paper develops LENS — Layered Evaluation with Noise and Systematic-bias — a single mathematical decomposition that derives all of them from one model. We write perceived quality as $\mathrm{logit}(\hat q) = \mathrm{logit}(q) + \beta^\top x + \varepsilon$: true quality, plus a feature-aligned systematic bias, plus random noise, all in log-odds space. From this one equation we derive the design principles practitioners reach for intuitively but cannot derive: why batch evaluation outperforms sequential review, why committee size reduces noise but not correlated bias, why the winner of competitive bidding overestimates, why architecture matters more than evaluator skill. The framework's parameters can be calibrated from real evaluation data. We do so on N = 35 startups with a ten-expert panel and find $\beta_{\mathrm{merit}} = 0.79$ and $\beta_{\mathrm{delivery}} = 0.297$ — systematic biases that survive ten-fold averaging, exactly as the framework predicts.

The contribution is not any single result. Each individual result is in the literature somewhere: Capen, Clapp & Campbell (1971) named the winner's curse; Kahneman, Sibony & Sunstein (2021) named noise; McPherson, Smith-Lovin & Cook (2001) named homophily. The contribution is that one decomposition explains all of them, that it has bite as a calibration target, and that it generates design rules — what we call **Human Decision-Systems Engineering (HDSE)** — for the multi-stage selection processes organizations actually run.

> **Data availability.** The underlying startup data is confidential. The closest reproducible analog of the calibration in §6 is [`code/paper1_calibration/calibrate_beta.py`](../code/paper1_calibration/calibrate_beta.py) running against [`code/data/startup_evaluations_avg_anon.csv`](../code/data/startup_evaluations_avg_anon.csv). The published $\beta_{\mathrm{merit}} = 0.79$, $\beta_{\mathrm{delivery}} = 0.297$ values come from a feature decomposition (substantive content vs. presentation style) on per-rater human judgments not present in the public anonymized data; the script computes the closest available alternative — a regression of expert score on AI-derived component scores — for the public reproduction case. See §6.4.
>
> **Sample size.** N = 35 is sufficient to demonstrate the framework's parameters can be estimated from real committee judgments and that systematic biases survive ten-fold averaging. Larger-N replication and per-rater identification of $\beta$ are out of scope; comprehensive simulation validation is in Paper 2.

**Keywords:** human decision systems, multi-stage selection, systematic bias, committee aggregation, order statistics, evaluator architecture, log-odds, venture capital.

---

## 0. Notation

The paper uses the following symbols throughout. The reader who prefers prose to symbols can skip this section and refer back as needed; everything is reintroduced in context where it first appears.

$q$ is the true success probability of a candidate (unknown to evaluators). $\hat q$ is an evaluator's perceived success probability. $\beta$ is the systematic bias vector — how an evaluator over- or under-weights the components of $x$ relative to their true predictive value. $x$ is the observable feature vector (credentials, presentation quality, demographics, prior signals). $\varepsilon$ is the random noise term (fatigue, mood, irreducible uncertainty). $i$ indexes candidates, $j$ indexes evaluators, $k$ is committee size, $n$ is candidate-pool size, $s$ is the number selected. $\rho_\beta$ and $\rho_\varepsilon$ are the cross-evaluator correlations of bias and noise respectively.

The model assumes evaluator biases are static within an evaluation period, that noise is conditionally independent of features given the systematic component (so $E[\varepsilon \mid x] = 0$), and that committee members form perceptions independently before aggregation. The framework applies when multiple evaluators assess candidates on bounded probability scales, observable features systematically influence judgments, and the architecture (committee structure, batch size, stage count) is something a designer can change. It applies less well when evaluators strategically misreport their beliefs, when bias parameters shift on faster timescales than the estimation window, when extreme selection rates push the analysis into tail behavior the linear approximation cannot capture, or when strong nonlinearities or interactions dominate the linear $\beta^\top x$ term.

---

## 1. Introduction

A founder pitches to ten venture firms over a two-month fundraising process. Three firms make offers. The founder accepts the highest valuation — fifteen percent above the second-best offer. The winning firm celebrates internally: they beat tier-one competitors for the deal. Two years later, the startup fails to find product-market fit and shuts down. The winning firm runs a post-mortem and concludes they were forty percent above fair value at entry. The partners ask one another: why do we keep losing money on deals we *win*?

Across the building, in a different industry, an HR executive runs a recruiting initiative explicitly designed for diversity. Blind résumé screening is implemented. Outreach is broadened to non-traditional channels. Three years later, the engineering team is ninety percent from the same demographic and educational background, despite no individual decision having had that goal. The director runs the same kind of post-mortem and concludes the team must have been unconsciously biased — though by every observable measure, they followed the procedure.

A grant program officer notices that the proposals winning their committee's review have a particular flavor — credentialed, conventional, from prestigious institutions. The committee was deliberately expanded from three members to twelve to fix this. The bias did not budge. The committee got more confident in its choices but did not change them.

These three cases are taken to be three different problems. The first is a story about discipline at the bidding table. The second is a story about unconscious bias in hiring. The third is a story about institutional capture. Each has its own folk-corrective: be more disciplined, run more bias training, expand the committee further. Each corrective is mostly ineffective. They are mostly ineffective because the underlying mechanism is the same in all three cases, and the folk-correctives target the wrong layer.

This paper introduces the framework that makes the underlying mechanism visible. We model perceived candidate quality as a noisy, biased perception of true quality, working in log-odds space so probabilities stay bounded:

$$\mathrm{logit}(\hat q) = \mathrm{logit}(q) + \beta^\top x + \varepsilon.$$

True quality $q$ is what the candidate actually delivers if selected. The evaluator never observes $q$ directly. They observe a transformed version, distorted by their own systematic over- and under-weightings of the candidate's features ($\beta^\top x$, where $\beta$ is the evaluator's bias vector and $x$ is the feature vector) plus random noise ($\varepsilon$). All of the puzzling patterns above — the winner's curse, the homogeneity trap, the committee paradox — fall out of this single decomposition, with no further moving parts.

The winner's curse is order statistics on $\varepsilon$: in $N$-way competition the bidder selected as the winner is mechanically the one whose perception was furthest above the average, so $E[\varepsilon_{\mathrm{winner}}] \approx \sigma_\varepsilon \sqrt{\log N}$. This is structural, not psychological, and it does not require any of the evaluators to be biased. The homogeneity trap is multiplicative compounding of small per-stage biases through a multi-stage pipeline: a bias of $0.2$ in log-odds per stage compounds to $e^{0.8} \approx 2.2 \times$ multiplicative advantage over four stages. The committee paradox is variance algebra under correlated $\beta_j$: averaging $k$ committee members reduces noise as $\sigma_\varepsilon / \sqrt{k}$ but reduces bias as $\sigma_\beta \sqrt{\rho_\beta + (1-\rho_\beta)/k}$, which only collapses to zero when the committee members' biases are uncorrelated.

These three results are not new. The winner's curse goes back to Capen, Clapp & Campbell (1971); homophily compounding to McPherson, Smith-Lovin & Cook (2001); the variance-of-correlated-averages formula to any standard statistics text. What is new is that one decomposition derives all of them, that the same decomposition keeps deriving the patterns when we apply it to batch evaluation, contrarian advantage, recommendation power, and stage-sequencing — and that the parameters $\beta$ and $\sigma_\varepsilon$ can be estimated from real evaluation data. The framework is not just an analytical lens; it is a calibration target.

What that calibration target gives us is the move from diagnosis to engineering. Diagnosing that a hiring committee is biased and should "do better" is what current practice produces. Engineering the hiring process to *minimize the conditions under which bias compounds across stages* is what the framework produces. We call the engineering practice **Human Decision-Systems Engineering (HDSE)**: the systematic, model-driven design of multi-stage selection processes that transform dispersed human judgments into high-quality collective decisions. Paper 2 of this series demonstrates HDSE in practice, simulating eleven investor archetypes and showing that platform architectures with good HDSE outperform elite venture firms with bad HDSE. Paper 3 instantiates the AI-filter component of one such platform.

The rest of this paper proceeds as follows. Section 2 places LENS in the disconnected literatures it draws from — operations research, behavioral economics, signal detection theory, organizational behavior, network theory — and shows what each provides that LENS uses, and what each lacks that LENS fills in. Section 3 develops the model formally, building from a simple error decomposition to the full log-odds form. Section 4 states the three load-bearing theorems: batch superiority, committee aggregation under correlated bias, and the winner's curse. Section 5 walks through the six phenomena named above plus three others, deriving each as a consequence of the model rather than treating them as separate puzzles. Section 6 calibrates the model on a real expert panel. Sections 7 and 8 discuss boundary conditions and the research agenda that connects this paper to Papers 2 and 3. Section 9 concludes.

A note on the order of arguments. We use the perception model informally in §1 and §5 before introducing it formally in §3. The reader who prefers the formalism first should read §3 before §5. Nothing in §5 is rigorous on its own; the work that makes the §5 patterns derivable is in §3 and §4.

---

## 2. Related Work

LENS sits at the intersection of five literatures that have evolved largely independently of one another. Each has produced sophisticated tools for some piece of the multi-stage selection problem. None has produced a unified framework that combines them.

**Wisdom of crowds and aggregation theory.** Galton's 1907 *Vox Populi* established the foundational result: 787 fairgoers' median estimate of an ox's weight (1,207 pounds) was within nine pounds of the true weight (1,198), demonstrating that aggregated judgments under independence and motivation can outperform individual experts. Condorcet's Jury Theorem (1785) gave the formal version: if individual accuracy exceeds 50% and errors are independent, group accuracy approaches certainty as group size grows. Page (2007) extended the result to diversity of perspective, showing that heterogeneity among aggregators is what drives the gain. These results assume single-stage aggregation with independent errors. They do not address what happens when aggregation runs across multiple sequential stages with correlated biases — which is the case in every real hiring, admissions, or investment process.

**Noise and bias decomposition.** Kahneman, Sibony & Sunstein (2021) is the most prominent recent treatment of the diagnostic problem: their decomposition of mean squared error into bias-squared plus noise-squared is the same starting point we take in §3, and their distinction among level noise (different evaluators run hot or cold), pattern noise (different evaluators weight features differently), and occasion noise (the same evaluator inconsistent across days) maps precisely onto the components of LENS. Their treatment is descriptive — they document the magnitude of the problem, including a famous result that 55% of insurance underwriters' premium estimates for identical cases fall outside a defensible range. The descriptive treatment stops short of an optimization framework: how should you design the architecture given the noise decomposition? That is the gap LENS addresses.

**Signal detection theory.** Green & Swets (1966) laid the foundations of how evaluators distinguish signal from noise under bounded uncertainty, separating sensitivity ($d'$) from response criterion ($\beta$). Receiver operating characteristic curves characterize the entire trade-off space. The Sequential Probability Ratio Test (Wald 1947) extends SDT to dynamic settings. The framework handles individual observers making binary decisions well; it has been less extensively applied to committees, multi-stage architectures, or evaluator pools with heterogeneous biases.

**Multi-stage screening in operations research.** Cooper's Stage-Gate process (1990) — adopted by roughly 80% of North American firms in some form — divides product or proposal evaluation into discrete stages with go/no-go gates. Empirical work shows substantially higher success rates for stage-gate adopters. Stochastic programming, optimal stopping (Smith & Nau, 1995), and real-options frameworks formalize when to advance versus reject as information accumulates. These models optimize information acquisition timing. They generally assume unbiased evaluators at each stage — a simplification that disappears in actual organizational settings.

**Committee theory and network effects.** Arrow's Impossibility Theorem (1963) and the social-choice literature characterize fundamental limits on preference aggregation. Empirical work on committee composition consistently identifies a sweet spot of five to nine members. Granovetter's (1973) "strength of weak ties" and the broader homophily literature (McPherson, Smith-Lovin & Cook, 2001) document how networks transmit information, opportunity, and selection bias simultaneously. Brooks et al. (2014) showed that identical pitches are rated differently when delivered by attractive men. Each of these is a piece of the architecture-design puzzle. None directly provides architecture-design rules for the multi-stage case.

The integration gap, then, is structural. Each tradition handles one piece. None takes seriously that real selection processes run across multiple stages with heterogeneous evaluator pools whose biases correlate, that observable features systematically distort perception, and that the architectural choices (batch size, committee composition, stage sequence, threshold rules) are the actionable design surface. LENS treats these together because, mathematically, they are part of the same system.

---

## 3. The LENS Model

The model develops in three steps. We start from the simplest plausible perception equation, identify its failure mode, and rewrite it in a form that captures multi-stage compounding correctly.

### 3.1 Why the Simple Error Model Is Not Enough

The natural first attempt at modeling perception error is additive on the probability scale: $\hat q_i = q_i + \delta_i$, with $E[\delta] = 0$ across evaluators. This is the implicit model behind Galton's ox-weight result. It works well for one-shot estimation problems where the only thing the modeler needs to capture is that individual estimates are noisy and average out to the truth.

It does not work well for multi-stage selection systems for two reasons. First, the equation assumes errors cancel under averaging — but Kahneman, Sibony & Sunstein document that systematic differences across evaluators persist no matter how many evaluators you aggregate. Second, $\hat q_i = q_i + \delta_i$ does not respect the bounded scale: probabilities live in $[0, 1]$, and adding a noise term to a probability near the boundary produces estimates that may exceed one or fall below zero. The model needs a transformation that keeps perception bounded and that captures the multiplicative way biases compound across stages.

### 3.2 The Decomposition

We separate the error into a systematic component (correlated with the candidate's observable features) and a random component (independent of features). Conditional on $x$, the law of total expectation gives

$$\delta_i = E[\delta_i \mid x_i] + (\delta_i - E[\delta_i \mid x_i]).$$

The right-hand side is decomposed exactly: by construction, the second term has zero conditional mean given $x$. We approximate the first term with its best linear predictor, $E[\delta_i \mid x_i] \approx \beta^\top x_i$, where $\beta$ minimizes $E[(\delta_i - \beta^\top x_i)^2]$ over the candidate population. This yields

$$\delta_i = \beta^\top x_i + \varepsilon_i,$$

where $\varepsilon_i$ is the residual random component with $E[\varepsilon_i \mid x_i] = 0$ by construction. The decomposition is general: any nonlinearity or interaction not captured by the linear form gets absorbed into $\varepsilon_i$, and we permit $\mathrm{Var}(\varepsilon_i \mid x_i)$ to vary with $x_i$ (heteroskedasticity). What it gives us is a clean separation of the *predictable* component of error (driven by features) from the *unpredictable* component (random across evaluation occasions).

The interpretation of $\beta$ is over- or under-reaction relative to true predictive value. If $\beta_{j, \mathrm{pitch}} > 0$, evaluator $j$ overweights pitch quality beyond what it actually predicts about success — pitch is a feature, but the true relationship between pitch and success is already absorbed into $q_i$, so $\beta_{j, \mathrm{pitch}}$ captures only the deviation. This is what makes $\beta$ identifiable: we are not estimating the relationship between pitch and success (which mixes feature predictiveness and bias), we are estimating the deviation from accurate weighting.

### 3.3 The Logit Transformation

The additive model on the probability scale violates probability bounds and does not capture compounding correctly. Following the generalized linear model framework (McCullagh & Nelder, 1989), we work in log-odds space:

$$\mathrm{logit}(\hat q) = \mathrm{logit}(q) + \beta^\top x + \varepsilon, \qquad \mathrm{logit}(p) = \log\frac{p}{1-p}.$$

This transformation does three things. First, $\hat q$ stays in $[0, 1]$ regardless of how large $\beta^\top x + \varepsilon$ becomes — the inverse logit (sigmoid) is bounded. Second, biases compound multiplicatively across stages rather than additively, which matches the empirical observation that homophily and prestige effects accumulate exponentially through interview chains. Third, the orthogonality condition $E[\beta^\top x \cdot \varepsilon] = 0$ carries through the transformation, which means the decomposition into systematic and random components remains identified after the transformation.

The map between the LENS components and the noise taxonomy of Kahneman, Sibony & Sunstein (2021) is direct: their level noise corresponds to between-evaluator variance in the intercept of $\beta_j$; their pattern noise corresponds to between-evaluator variance in the feature loadings of $\beta_j$; their occasion noise corresponds to within-evaluator variance in $\varepsilon_{ij} \mid x_i$. The diagnostic and the engineering vocabulary are the same vocabulary; LENS adds the engineering moves.

### 3.4 From One Evaluator to a Committee

When $k$ evaluators form a committee and average their log-odds perceptions, the systematic and random components separate cleanly. The committee's perception is

$$\mathrm{logit}(\hat q_{\mathrm{committee}}) = \mathrm{logit}(q) + \bar\beta^\top x + \bar\varepsilon,$$

with $\bar\beta = \frac{1}{k} \sum_j \beta_j$ and $\bar\varepsilon = \frac{1}{k} \sum_j \varepsilon_j$. Under conditional independence of the noise terms, $\mathrm{Var}(\bar\varepsilon) = \sigma_\varepsilon^2 / k$ — the standard wisdom-of-crowds reduction. But the systematic average $\bar\beta$ converges to the population mean of evaluator biases. If all evaluators share a background that produces correlated bias toward, say, candidates from prestigious institutions, then $\bar\beta$ does not approach zero. The committee is more confident (lower variance) but no less biased (same expected $\bar\beta$). Precision without accuracy.

This is where the architectural choice becomes load-bearing. Adding committee members reliably reduces random noise, which is the one thing committees were designed for. It does almost nothing to systematic bias unless the members are *bias-diverse* — which is to say, unless their $\beta$ vectors point in different directions. Demographic diversity is a proxy for bias diversity; it is sometimes the right proxy and sometimes not. The framework makes the distinction precise: the relevant quantity is $\rho_\beta$, the correlation of bias vectors across the committee, and the formula for residual systematic bias is

$$\mathrm{Var}(\bar\beta) = \sigma_\beta^2 \left[ \rho_\beta + \frac{1 - \rho_\beta}{k} \right].$$

When $\rho_\beta \approx 0$, the committee size $k$ does the work that the wisdom-of-crowds intuition says it should. When $\rho_\beta \approx 1$, committee size does nothing and the bias persists. The effective committee size for bias reduction is $k_{\mathrm{eff}} \approx 1 / (1 - \rho_\beta)$, which means a panel of twelve members with high bias correlation is operationally a panel of two or three.

---

## 4. Theorems and Design Rules

The model produces three results that anchor the rest of the paper. They are the load-bearing claims; everything in §5 derives from them, and the calibration in §6 estimates the parameters they take as inputs.

**Theorem 1 (Batch evaluation superiority).** *Consider selecting $k$ candidates from $n$ where perception errors $\varepsilon_i$ are independent with variance $\sigma_\varepsilon^2$. Batch evaluation — ranking candidates by perceived quality and selecting the top $k$ — achieves expected quality advantage over sequential evaluation (accepting the first $k$ candidates exceeding a fixed threshold) of approximately*

$$E[\Delta_{\mathrm{quality}}] \approx \sigma_\varepsilon \cdot \left[\Phi^{-1}\!\left(\frac{n-k+1}{n+1}\right) - \Phi^{-1}\!\left(\frac{k}{n}\right)\right],$$

*where $\Phi^{-1}$ is the inverse standard normal CDF.* The intuition is that batch evaluation lets the order statistic do work the threshold cannot: when comparison information is available, the top-$k$ candidates of a noisy ranking are systematically better than the first $k$ candidates that exceed a noisy threshold, because thresholding cannot benefit from the among-survivors comparison. For selecting the top 2% of candidates, the batch advantage is roughly $0.9 \sigma_\varepsilon$ in log-odds, which translates into substantial true-quality improvement.

**Theorem 2 (Committee aggregation under correlated bias).** *For committee size $k$ with bias correlation $\rho_\beta$ and noise correlation $\rho_\varepsilon$,*

$$\mathrm{Var}(\bar\beta) = \sigma_\beta^2 \left[\rho_\beta + \frac{1-\rho_\beta}{k}\right], \qquad \mathrm{Var}(\bar\varepsilon) = \sigma_\varepsilon^2 \left[\rho_\varepsilon + \frac{1-\rho_\varepsilon}{k}\right].$$

This is the formal version of the committee paradox: random noise drops as expected with committee size, but systematic bias is bounded below by $\sigma_\beta^2 \rho_\beta$ regardless of how many members you add. The result is standard variance algebra; what makes it load-bearing for design is that it gives the architect a target — measure $\rho_\beta$ in your evaluator pool and decide whether adding members is doing what you think it is doing.

**Theorem 3 (Winner's curse in competitive selection).** *Under zero mean bias ($E[\beta^\top x] = 0$) and independent noise $\varepsilon_i \sim \mathcal N(0, \sigma_\varepsilon^2)$, the expected overestimation of the winning bidder in $N$-way competition satisfies*

$$E[\varepsilon_{\mathrm{winner}}] \approx \sigma_\varepsilon \cdot \Phi^{-1}\!\left(\frac{N}{N+1}\right) \approx \sigma_\varepsilon \sqrt{2 \log N}.$$

For two competitors the overestimation is roughly $0.56 \sigma_\varepsilon$; for ten competitors, $1.54 \sigma_\varepsilon$; for fifty, $2.25 \sigma_\varepsilon$. This is structural: it does not require any of the bidders to be biased, only that they have any noise at all. Competitive selection mechanically picks the bidder furthest above the mean. The intuitive reading is that any bidder who *wins* in a competitive process should discount their own valuation by the expected order-statistic of their noise distribution before treating their bid as fair value.

A fourth result, less central but useful in design, is that for a two-stage system with evaluation costs $C_1, C_2$ where $C_2 \gg C_1$, the optimal advancement rate is approximately $s \approx \sqrt{C_1 / C_2}$. If late-stage evaluation costs a hundred times more than early-stage, advance roughly ten percent of candidates from the early stage. The square-root form comes from balancing type-I error costs (rejecting good candidates early) against type-II error costs (wasting expensive evaluation on weak candidates).

The design rules these theorems imply are straightforward and largely intuitive once stated, but each is a place where current practice routinely gets it wrong: use batch evaluation when comparison is cheap; sequence stages by information cost ratio (cheap filters first, expensive evaluation for finalists); diversify the *biases* in your evaluator pool, not just the demographics; never let single evaluators veto candidates in early stages; calibrate thresholds to base rates; reserve a strategic fraction of capacity for explicitly contrarian selection. Each of these comes out of the framework as a formal consequence rather than as practitioner heuristic.

---

## 5. The Phenomena, Derived

Practitioners across domains have named the phenomena LENS explains. None of the names is wrong. What was missing was the recognition that they are consequences of the same underlying model. We walk through them in this section, noting which theorem from §4 each derives from, and pointing out where current folk-explanations get the mechanism right and where they get it wrong.

The **winner's curse** is the cleanest case. A startup pitches to ten venture firms; three offer term sheets; the founder accepts the highest offer; the deal underperforms. The folk explanation is that the winning firm got too excited. The structural explanation is Theorem 3: when ten evaluators with independent noise each estimate the same true quality, the highest estimate is mechanically the largest positive deviation, and it is on average $1.54 \sigma_\varepsilon$ above the true value. For an evaluator with noise standard deviation $\sigma_\varepsilon = 0.5$ in log-odds units and a true success probability of twelve percent, the winning firm's perceived probability is around twenty-three percent — almost double the true value. The folk explanation locates the failure in the firm's discipline; the structural explanation locates it in the architecture of the bidding process. Discipline cannot fix order statistics. The only fix is to discount the winning bid by the expected order-statistic correction, or to reduce competition (which sellers do not want), or to share the deal across multiple winners, which averages instead of maximizing the noise.

The **contrarian advantage** comes from the asymmetric quality bar bias imposes. When group consensus creates a positive bias toward consensus startups ($\beta_{\mathrm{consensus}} > 0$) and a negative bias against contrarian ones ($\beta_{\mathrm{contrarian}} < 0$), the funding threshold $\mathrm{logit}(\hat q) > -4.6$ requires the contrarian startup to clear a higher bar of true quality. If $\beta_{\mathrm{consensus}} = +0.7$ and $\beta_{\mathrm{contrarian}} = -0.7$, contrarian startups must be roughly four times more likely to succeed to receive the same evaluation. The portfolio-level consequence is that contrarian portfolios, conditional on being funded, have systematically higher true quality than consensus portfolios. The folk explanation that contrarian investors are smarter than consensus investors is not necessarily wrong — but it is not what is doing the work. What is doing the work is that the bias creates a higher-quality filter on contrarian deal flow. Kerr, Lerner & Schoar (2014) document above-average reported returns in contrarian angel financings consistent with this mechanism.

The **homogeneity trap** is the case where multiplicative compounding through stages creates outcomes nobody intended. A small per-stage bias toward candidates from a shared background — perhaps $\beta_{\mathrm{shared}} = +0.2$ in log-odds, an effect so small no individual evaluator would identify it — accumulates across four interview stages to $+0.8$ in log-odds, which is $e^{0.8} \approx 2.2 \times$ multiplicative advantage. As the team's composition shifts toward the shared background, more interviewers share the bias, the per-stage $\beta$ effectively grows, and the system enters a runaway feedback loop where the next hire is even more likely to share the background than the last one. The folk explanation is unconscious bias on the part of individual interviewers, which is correct as a description but not as a target for intervention. Bias training reduces the per-stage $\beta$, but it does not address the multiplicative compounding through stages, which is the mechanism that turns small biases into large outcomes. McPherson, Smith-Lovin & Cook (2001) document homophily; the framework here adds why the small per-stage effects compound to large terminal effects. The architectural fix is to reduce the number of stages where the bias can compound (fewer interviews, more parallel evaluation) and to introduce stages with deliberately uncorrelated bias profiles (interviewers from different backgrounds making independent rather than sequential judgments).

The **batch evaluation advantage** is Theorem 1 made concrete. Y Combinator's Demo Day presents 200+ startups in a single event. Techstars runs cohort-based accelerators. Elite venture firms hold "batch office hours" reviewing 10–15 pitches per session. Even individual angel investors often wait to evaluate deals in monthly batches rather than one at a time. The folk reading of this pattern is logistical convenience. The structural reading is that batch evaluation lets the order statistic do work the threshold cannot. Sequential evaluation suffers from threshold drift (the evaluator's calibration varies with what they have just seen) and from comparison impossibility (without simultaneous comparison, the evaluator cannot tell whether this candidate is top-five-percent or top-fifteen). Batch evaluation eliminates both. The expected quality gain for selecting the top two candidates from ten is approximately $0.5 \sigma_\varepsilon$ in log-odds, which translates into a true-success-probability gain from roughly seven to twelve percent. The pattern is not about logistics; it is about the mechanics of selection under noise.

The **committee paradox** is Theorem 2 made concrete. An academic hiring committee expands from three to twelve members to increase the diversity of opinion. Despite quadrupling the committee size, the department continues to hire the same profile: theorists over systems researchers, candidates from prestigious institutions over equally qualified candidates from less prestigious ones. The folk reading is that the committee culture is "too strong" and needs more diverse membership. The structural reading is that variance reduction in $\bar\beta$ is bounded below by $\sigma_\beta^2 \rho_\beta$. If all twelve members share the same bias profile (same training, same sub-field, same prestige sensitivities), then $\rho_\beta \approx 0.9$, and the effective committee size for bias reduction is $k_{\mathrm{eff}} \approx 10$. Adding the eleventh and twelfth members buys nothing. Worse, the random-noise reduction from twelve members (down to roughly $0.29 \sigma_\varepsilon$ from individual $\sigma_\varepsilon$) makes the committee more confident in its biased choices. Precision without accuracy. The fix is to recruit committee members whose $\beta$ vectors point in different directions — practically, this means recruiting from different sub-fields, different career stages, different methodological traditions — not to keep adding members from the same population.

The **disproportionate power of recommendations** completes the catalog. A cold email to a top venture firm gets a one-to-two percent response rate. A warm introduction from a trusted operator gets fifty percent. Employee referrals are hired at three times the rate of job-board applicants. The folk reading is that recommendations signal trust, that humans favor people they know, that warm introductions are a heuristic for quality. The structural reading is that recommendations function as cost-free first-stage filters with biases aligned to the second-stage evaluator's biases. When a recommender pre-screens 200 candidates in their network and forwards 20 to an evaluator, this is operationally equivalent to inserting an unpaid Stage 0 in front of the evaluator's actual screening process, with $\beta_{\mathrm{recommender}} \approx \beta_{\mathrm{evaluator}}$ (the alignment is what makes the introduction warm). The efficiency gain is dramatic — 95–99% of screening cost eliminated — but the bias amplification is also dramatic. The recommender's network shares background and biases with the evaluator's network (homophily), so the recommendations amplify the same biases that drive the homogeneity trap. The efficiency of recommendation-driven hiring is precisely the mechanism by which it produces culturally uniform outcomes. There is no contradiction between the efficiency gain and the bias amplification; they are two sides of the same architectural property.

These six phenomena are not the full set. The framework also explains, more briefly: why prestige effects compound across academic generations; why interview rubrics are weaker than they look (they shrink $\sigma_\beta$ but rarely change $\rho_\beta$); why "blind review" mitigates pattern noise but not level noise; why the optimal investment portfolio under bias is more diversified than it looks under unbiased portfolio theory. We discuss each briefly in the appendix that accompanies the journal version. The pattern across all of them is the same: a phenomenon that current practice treats as either inevitable or as a personal failing turns out to be a derivable consequence of the architecture, and the architecture is something a designer can change.

---

## 6. Calibration

The framework is only as useful as its parameters are estimable. This section calibrates $\beta$ and the residual noise on a real expert panel — a partial calibration, by design — to demonstrate the parameters are recoverable from data the kind of organization that actually runs these processes already collects.

### 6.1 Data and Approach

The calibration uses N = 35 startups evaluated by the Cyrannus expert panel during a single round, with at least ten independent reviewers per startup. The dependent variable is the committee mean score on a 1–5 scale, which serves as a high-reliability outcome that isolates systematic effects from idiosyncratic individual noise. The committee aggregation is itself useful diagnostically: averaging ten independent evaluators reduces the random component of error by roughly $\sqrt{10} \approx 3.2$, so any systematic effect that survives the averaging is, by construction, not random noise.

The features available to the model are merit (a substantive measure derived from the panel's assessment of business quality, traction, team capability) and delivery (a presentational measure derived from the panel's assessment of pitch quality, clarity, polish). These two features were chosen because they correspond to the operational distinction Cyrannus uses internally between *startup quality* (what the business will be worth) and *pitch quality* (how well the founder presented it). Both features were normalized to the unit interval before estimation to make the resulting $\beta$ values directly comparable.

We estimate two specifications. The first regresses committee mean on merit alone, which by construction yields $\beta_{\mathrm{merit}} = 1.0$ — merit is the primary predictor and the regression coefficient absorbs the entire scale. The second regresses on merit and delivery jointly, which is the specification of interest: it asks how much delivery influences perceived quality *over and above* what merit predicts. If LENS is right that delivery operates as a systematic feature bias, $\beta_{\mathrm{delivery}}$ should be positive and statistically significant.

### 6.2 Results

The joint regression yields $\beta_{\mathrm{merit}} = 0.79$ (SE = 0.097, p < 0.001) and $\beta_{\mathrm{delivery}} = 0.297$ (SE = 0.097, p = 0.004). The adjusted $R^2$ is 0.76; the regression standard error is 0.89. The point estimates, the significance, and the model fit all support the framework's prediction that delivery operates as a positive systematic bias on perceived quality even after controlling for merit.

The merit coefficient of 0.79 represents a systematic attenuation: relative to its predictive role when delivery is omitted ($\beta_{\mathrm{merit}} = 1.0$ in the merit-only specification), merit is roughly 21% under-weighted by the panel when delivery is in the prediction set. The delivery coefficient of 0.297 represents the incremental influence of presentation on perceived quality. In log-odds units, these are economically meaningful effects: a one-standard-deviation improvement in delivery shifts perceived quality by approximately 0.3 log-odds units, which translates into a meaningful change in funding probability for candidates near the threshold.

The robustness checks tell the same story. A 1,000-replication bootstrap places the 95% confidence interval for $\beta_{\mathrm{delivery}}$ at $[0.11, 0.48]$ — well above zero. Five-fold cross-validation gives an out-of-sample $R^2$ of 0.72, indicating the model generalizes within this sample. A permutation test that shuffles delivery scores produces $p = 0.002$, ruling out the possibility that the delivery effect is a spurious correlation. Variance inflation factors are all below 1.5, ruling out multicollinearity between merit and delivery as a concern.

### 6.3 What the Numbers Mean

The headline finding is that the delivery effect ($\beta_{\mathrm{delivery}} = 0.297$) survives ten-fold averaging across an independent expert panel. This is the framework's central diagnostic prediction. If delivery were noise — if individual evaluators' susceptibility to pitch quality were random across evaluators — then averaging across ten reviewers should have driven the coefficient toward zero, the way wisdom-of-crowds aggregation drives random errors toward zero. It did not. The delivery effect is a *correlated* bias: most evaluators on the panel weight delivery in the same direction, so the averaging cannot wash it out. This is exactly Theorem 2's prediction — random noise reduces with committee size, systematic bias does not.

The merit attenuation ($\beta_{\mathrm{merit}} = 0.79$ instead of 1.0) is consistent with the same diagnosis. When delivery is added to the model, it absorbs roughly 21% of the variance previously attributed to merit. The most plausible interpretation is that some fraction of what the panel perceives as merit is actually being driven by delivery — a candidate with strong delivery is rated as having stronger merit even after controlling for their actual underlying quality. This is the classic confound the framework predicts: an observable feature (delivery) systematically distorts perceptions of an unobservable quality (merit), and the distortion persists across the panel because the panel members share the bias.

### 6.4 Limitations and What Reproduces from Public Data

The calibration above used per-rater human judgments of merit and delivery — the kind of granular score data Cyrannus collects internally during expert panels. That data is confidential and is not part of this paper's public release. The closest reproducible analog is a regression of committee mean expert score on AI-derived component scores (market potential, solution viability, team capability, initial traction), which can be run end-to-end against the anonymized data in [`code/data/startup_evaluations_avg_anon.csv`](../code/data/startup_evaluations_avg_anon.csv) using the script [`code/paper1_calibration/calibrate_beta.py`](../code/paper1_calibration/calibrate_beta.py).

The public reproduction is a different specification — AI-component features rather than human merit/delivery — and so produces different $\beta$ values that should not be confused with the merit/delivery results above. What it does reproduce is the model fit ($R^2 = 0.745$ in the public version) and the qualitative pattern that the largest single coefficient is on the substantive feature (market potential) with smaller but non-trivial coefficients on the others. The journal version will include both calibrations side by side.

Beyond data access, the calibration has four limitations that bound how strongly the results should be read. Committee-aggregated outcomes mask individual-evaluator heterogeneity, so we cannot identify per-evaluator $\beta_j$ or measure $\rho_\beta$ directly from this data — that would require per-rater scores, which a properly designed follow-up could extract. The observational design prevents causal claims; we demonstrate association consistent with framework predictions, not causation. A single domain (startup evaluation) is a single test, and generalization to hiring, admissions, and grant review is the work of Papers 2 and 3 plus future replication studies. The interpretation of $\beta_{\mathrm{merit}} = 0.79$ as "21% attenuation" assumes merit and delivery are on comparable scales, which they are by construction in this specification but which would deserve sensitivity analysis in a journal-length presentation.

What the calibration establishes, despite the limitations, is that the framework's parameters are estimable from the kind of evaluation data organizations already collect, and that the specific prediction LENS makes — systematic feature biases survive committee aggregation — holds in this dataset. The comprehensive parameter estimation across architectures and evaluator types is the work of Paper 2's simulation framework.

---

## 7. Boundary Conditions

The framework is not universally applicable. It targets a specific class of selection problems with specific structural properties, and it fails outside that class.

LENS applies when multiple evaluators assess candidates on outcomes that admit a probability interpretation, when observable features systematically influence those judgments, when the architecture (committee structure, batch sizes, stage counts, threshold rules) is designable rather than fixed, and when outcomes are eventually observable for calibration. Hiring, venture investment, university admissions, and grant review fit cleanly. So do less obvious cases like clinical trial enrollment, judicial sentencing, and editorial decision-making at peer-reviewed journals.

It applies less cleanly when evaluators strategically misreport their beliefs. The model assumes evaluators report their honest perception; if they vote strategically to manage committee dynamics or to manipulate the outcome, the formal results break down. Game-theoretic extensions exist in the social-choice literature; they are not part of LENS. It applies less cleanly when bias parameters shift on faster timescales than the estimation window — a venture market in which what investors consider "hot" changes monthly will produce non-stationary $\beta$ that the estimation cannot track. Dynamic Bayesian extensions are the natural fix and would constitute a sequel paper. It applies less cleanly when extreme selection rates push the analysis into tail behavior the linear approximation cannot capture; selecting the top 0.1% of candidates is a different mathematical problem than selecting the top 10%, and the Gaussian approximations underlying the order-statistic results in Theorems 1 and 3 break down when the tail thickness matters. Extreme value theory provides the right tools and they are not what this paper develops.

A second class of failure is identifiability. The framework is identified when there is variation in features across the candidate pool, when there are multiple evaluators per candidate (so $\beta$ and $\varepsilon$ can be separated), and when at least some outcomes are observable for parameter calibration. None of these conditions is exotic, but each fails in specific real-world settings. A single-evaluator process cannot separate systematic from random error; this is not a weakness of the framework, it is a fundamental limit of what can be inferred from one judgment. A candidate pool with no feature variation cannot identify $\beta$; this is a sample-design problem, fixable by including a sufficiently diverse pool. A process with no observable outcomes (because it is too new, or because outcomes are inherently subjective) limits the calibration to bias decomposition without ground truth.

The practical diagnostic for whether LENS applies in a particular setting is straightforward. Is the evaluation on a probability scale? Are the evaluators' biases systematic in the framework's sense — do similar candidates get rated similarly across evaluators in ways that correlate with observable features? Do outcomes eventually exist that allow calibration? Is the architecture actually designable, or is it institutionally fixed in ways that defeat the purpose? A "yes" to all four supports applying the framework. A "no" to any of them is a reason to either narrow the scope (calibrate what can be calibrated, design what can be designed) or to use a different framework entirely.

---

## 8. Research Agenda and Trilogy Position

This paper establishes the theoretical foundation and a demonstrative calibration. The two pieces missing for a complete picture — comprehensive validation of architectural predictions, and operational instantiation of those predictions in a working system — are the work of the companion papers.

Paper 2, *The Platform Paradox: When Angels with Architecture Outperform Elite VCs*, validates the framework through Monte Carlo simulation across eleven investor archetypes (solo angels, angel groups, accelerators, syndicates, general venture firms, elite venture firms, platform variants). Across 2,200 configurations spanning four candidate-quality tiers, three evaluator profiles, and multiple architectural variants, the simulation produces the central empirical finding the framework predicts: architecture matters more than individual evaluator skill. A platform-enabled angel achieves 3.91% portfolio quality, beating elite venture firms (3.51%) and individual angels (1.50%) by 160% — the gain comes from the multi-stage architecture (scout, AI filter, expert committee), not from the angel's enhanced ability. Paper 2 also introduces selection consistency (coefficient of variation across runs) as a third performance dimension alongside quality and scale, and shows platforms achieve six times better consistency than traditional venture architectures.

Paper 3, *Instruction Distillation for Startup Pitch Ranking*, instantiates the AI-filter component of Paper 2's platform architecture in a working system. A large language model, prompted with a methodology distilled from a ten-expert evaluation panel, ranks startup pitches in alignment with the panel at NDCG@20 = 0.923. The methodological contribution is *instruction distillation*: rather than asking experts to articulate their criteria, we have an LLM read pairs of (pitch, expert review) and reverse-engineer the implicit rubric. The architectural contribution is that the LLM is positioned as a first-stage filter, not as a replacement for human judgment, with the human expert as the final stage. The empirical NDCG numbers from Paper 3 feed back into Paper 2's sensitivity analysis as the realistic noise parameter for the AI-filter stage, closing the loop between the simulation predictions and the operational reality.

Beyond the trilogy, the natural extensions are along five axes. *Per-rater identification of $\beta_j$* requires data with sufficient evaluator-candidate cross-coverage that individual-evaluator bias profiles can be estimated separately from candidate-level effects, which the current calibration does not have. *Dynamic $\beta(t)$* would relax the static-bias assumption to allow tracking of how evaluators' biases drift across markets, time periods, or training interventions. *Architectural search* — formal optimization over the space of designable architectures (committee sizes, stage counts, threshold rules) given measured $\beta$ and $\sigma$ — is the engineering question this paper sets up but does not solve in closed form. *Cross-domain replication* of the calibration in domains beyond venture investment is the most important external-validity question, and the most tractable for follow-up work. *Strategic-evaluator extensions* into the game-theoretic regime where evaluators may misreport their beliefs is the formal-modeling extension that connects LENS to the social-choice literature.

The connections to adjacent fields are also worth naming briefly. To economic theory: LENS is a framework for treating selection mechanisms as designable rather than as exogenous market outcomes, which is the closest the paper comes to a market-design contribution. To machine learning: the architectural results in §4 have direct analogs in ensemble methods (committee aggregation), boosting (sequential weak learners), and active learning (which selection criteria pick the most informative candidates). To organizational behavior: the homogeneity-trap and committee-paradox derivations give formal grounding to qualitative patterns the field has documented for decades. To causal inference: the identification challenges around $\beta$ — separating selection bias from treatment effects, finding instruments for unobserved quality — are exactly the challenges the modern causal-inference literature has developed tools for, and LENS sits as an applied case study where those tools should be useful.

---

## 9. Conclusion

Organizations spend a great deal on selection systems, then run them on intuition and folk-correctives. The hiring committee that produces homogeneous outcomes is told to expand. The venture firm that lost money on a competitive deal is told to be more disciplined. The grant program that funds the same profile year after year is told to recruit more diverse reviewers. Each of these correctives misses the architectural mechanism that produced the outcome.

LENS makes the mechanism visible. One equation — perceived quality decomposes into true quality plus a feature-aligned systematic bias plus random noise, in log-odds space — derives the patterns: the winner's curse from order statistics on $\varepsilon$; the homogeneity trap from multiplicative compounding of $\beta$ across stages; the committee paradox from variance algebra under correlated $\beta_j$; batch superiority from order statistics on $\hat q$; recommendation power from cost-free Stage 0 with aligned $\beta$. None of these is new individually; the contribution is that they are the same model.

What the framework gives, beyond the unification, is a calibration target. The parameters $\beta$ and $\sigma_\varepsilon$ can be estimated from the kind of evaluation data organizations already collect — we do this on N = 35 startups and find delivery bias surviving ten-fold averaging at $\beta_{\mathrm{delivery}} = 0.297$, exactly as the framework predicts. The calibrated framework is what the design rules of §4 and §7 are *for*: not as folk wisdom about how to run committees, but as architectural choices made with measured parameters.

The three patterns the rest of the LENS trilogy validates and operationalizes are best stated together. Architecture matters more than individual evaluator skill (Paper 2). The AI-filter stage of a platform architecture can be instantiated in a working system at NDCG@20 = 0.923 alignment with a ten-expert panel (Paper 3). And the framework that ties them both to a single equation is the framework this paper develops.

Two final observations. The first is that this paper, like every paper, was produced by a process — peer review, editorial selection, citation politics, the same publication architecture LENS describes — that the framework predicts is subject to the dynamics it documents. We do not exempt our own production. The framework recommends architectural fixes that we are in no position to implement on our own discipline; it does, however, recommend reading the patterns it describes with the same skepticism wherever they show up, including in how this paper found its way into your hands.

The second is that the engineering practice the paper proposes — Human Decision-Systems Engineering — is a name for what good practitioners already do partially and intuitively. Y Combinator's batch evaluation. Cyrannus's multi-stage screening. Elite venture firms' partner-meeting protocols. The framework does not invent the practice; it makes it precise enough to teach, to compare, to optimize, and to test against alternatives. That is the move from craft to engineering, and the rest of the trilogy is what that move looks like in detail.

---

## References

Arrow, K. J. (1963). *Social Choice and Individual Values* (2nd ed.). Yale University Press.

Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? In *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency* (pp. 610–623). ACM.

Brooks, A. W., Huang, L., Kearney, S. W., & Murray, F. E. (2014). Investors prefer entrepreneurial ventures pitched by attractive men. *Proceedings of the National Academy of Sciences*, 111(12), 4427–4431.

Capen, E. C., Clapp, R. V., & Campbell, W. M. (1971). Competitive bidding in high-risk situations. *Journal of Petroleum Technology*, 23(6), 641–653.

Casella, G., & Berger, R. L. (2002). *Statistical Inference* (2nd ed.). Duxbury.

Chen, D., Moskowitz, T. J., & Shue, K. (2016). Decision making under the gambler's fallacy: Evidence from asylum judges, loan officers, and baseball umpires. *Quarterly Journal of Economics*, 131(3), 1181–1242.

Condorcet, N. de. (1785). *Essai sur l'application de l'analyse à la probabilité des décisions rendues à la pluralité des voix.* Imprimerie Royale.

Cooper, R. G. (1990). Stage-gate systems: A new tool for managing new products. *Business Horizons*, 33(3), 44–54.

Galton, F. (1907). Vox populi. *Nature*, 75(1949), 450–451.

Granovetter, M. S. (1973). The strength of weak ties. *American Journal of Sociology*, 78(6), 1360–1380.

Green, D. M., & Swets, J. A. (1966). *Signal Detection Theory and Psychophysics.* Wiley.

Kahneman, D., Sibony, O., & Sunstein, C. R. (2021). *Noise: A Flaw in Human Judgment.* Little, Brown Spark.

Kerr, W. R., Lerner, J., & Schoar, A. (2014). The consequences of entrepreneurial finance: Evidence from angel financings. *Review of Financial Studies*, 27(1), 20–55.

McCullagh, P., & Nelder, J. A. (1989). *Generalized Linear Models* (2nd ed.). Chapman & Hall.

McPherson, M., Smith-Lovin, L., & Cook, J. M. (2001). Birds of a feather: Homophily in social networks. *Annual Review of Sociology*, 27, 415–444.

Page, S. E. (2007). *The Difference: How the Power of Diversity Creates Better Groups, Firms, Schools, and Societies.* Princeton University Press.

Smith, J. E., & Nau, R. F. (1995). Valuing risky projects: Option pricing theory and decision analysis. *Management Science*, 41(5), 795–816.

Surowiecki, J. (2004). *The Wisdom of Crowds.* Doubleday.

Thaler, R. H. (1988). Anomalies: The winner's curse. *Journal of Economic Perspectives*, 2(1), 191–202.

Wald, A. (1947). *Sequential Analysis.* Wiley.

Wooldridge, J. M. (2010). *Econometric Analysis of Cross Section and Panel Data* (2nd ed.). MIT Press.
