# LENS Paper Style Guide

This guide governs the three papers in the LENS trilogy. It is adapted from `guidelines/tycheism_paper_style_guide.md` and from the worked example `C:\Users\mikea\SCRIPTS\tycheism_repo\papers\paper_a_trajectory_divergence.md`. The principles are the same; the examples are LENS.

The version-1 drafts of the LENS papers were structured as enumerations: numbered "Six Phenomena", bulleted "What practitioners observe / What practitioners think / The deeper truth", three-line "Design Implications" lists, table after table. Bullet structure is appropriate for reference manuals and for slide decks. It is not appropriate for an argumentative paper. The reader of a paper should feel an argument building, not be handed a shelf of items. This guide is the rule set for converting bullet structure into flowing prose without losing the rigor.

---

## The Core Rule

**Lead with the human version, then name the formal object.**

Not: "Var(β̄) = σ²_β [ρ_β + (1 − ρ_β)/k] characterizes the residual systematic bias under k-fold committee aggregation."

Instead: "Adding more people to a hiring committee reduces random disagreement but does almost nothing to the shared blind spots — the systematic bias survives the average. The variance formula explains why."

The reader has to land the point before they hit the formula. If they cannot restate the idea in their own words after the prose version, the formula will let them nod without understanding.

---

## Readability Rules

### One idea per paragraph

If a paragraph turns ("But," "However," "What this means in practice is…"), it needs a line break before the turn. Two ideas in one paragraph means neither lands. The Tycheism rule applies unchanged.

### Concrete before abstract

Every formal claim follows a sentence the reader can picture. "A startup pitches to ten VCs and the one that bids highest tends to be the one that overestimated by the most" before "E[ε_winner] ≈ 1.5 σ_ε for N = 10 competitors." The numerics are the second sentence, not the first.

### Kill the "What practitioners observe / think / the deeper truth" template

The v1 papers used this three-bullet template for every phenomenon. It is a journalism device that signals to the reader that what follows is a mini-essay rather than part of the paper's argument. Rewrite each phenomenon as flowing prose: name the pattern in one paragraph, name the practitioners' folk explanation in one sentence inside the next paragraph, and devote the rest of the section to the actual mechanism. The reader does not need three bolded labels to follow a single example.

### Kill the "Six Phenomena" enumeration

Six numbered sub-subsections, each with the same structure, reads as a catalog. A catalog is fine in §3 once the framework is on the table — at that point, you are inviting the reader to scan. But the *introduction* of LENS through the phenomena should be a single section that develops the family of patterns through three or four illustrative examples in continuous prose. The remaining phenomena can be summarized briefly and pointed at, not exhaustively enumerated up front. Treating all six phenomena as equally important in the introduction is the same mistake the abstract makes when it lists every result.

### One-paragraph subsections are paragraphs that got promoted

If a subsection contains one paragraph, fold it into the parent or merge with an adjacent subsection. The test: remove the subsection header. Does the paragraph still flow naturally? If yes, the header is reference-manual cruft. The v1 papers had several `### 6.5 Limitations of Calibration` headers that contained a single paragraph each.

### Tables earn their ink

A table in a LENS paper belongs there only when the reader needs to look up a number, not when the writer needed scaffolding. Two cases qualify: parameter lists (one row per parameter, useful for reproduction) and result summaries that compare more than three conditions on the same metrics (NDCG@k across setups; archetype quality across configurations). Everything else — the noise-taxonomy table, the "what practitioners think vs. the deeper truth" two-column tables — should be prose. The v1 Paper 1 has a "Noise Type | Description | LENS Component" table whose three rows can be a single paragraph.

### Numbers earn their ink

A specific number belongs in the main text only if removing it would weaken the argument. The reader needs the *relationship* (higher, lower, comparable, dramatically different) more often than they need the fourth decimal place. Reserve precise numerics for: (a) the headline result that anchors the paper (NDCG@20 = 0.923; platform 3.91% vs elite VC 3.51%), (b) parameters that are needed for reproduction, (c) numbers that distinguish between two competing interpretations. Everything else: state the relationship.

### The abstract is a pitch, not a table of contents

Lead with the result that makes the paper matter. The v1 LENS abstract opened by listing six phenomena. The reader who stops after paragraph one should still know the central claim: *the same equation explains six things, and that gives you design principles you didn't have before.* Paper 2's abstract should lead with "architecture beats ability." Paper 3's abstract should lead with "LLM ranking aligns with expert ranking at NDCG@20 = 0.923." Save the supporting list for the body.

### Say it once, well

If the same caveat appears in three sections with different hedging, the reader gets suspicious that you don't trust your own argument. State each caveat once in the place it most belongs. (Exception: the *central claim*, which builds through reappearance — see "Thread the central claim" below.) The v1 papers say "comprehensive validation appears in Paper 2" three or four times. Once is enough.

### Earn every forward reference

"As developed in §6" costs the reader trust. Either give them enough to act on now, or cut the reference. The v1 papers point forward to appendices that did not exist when the reader got there.

---

## Structural Rules

### The paper is an argument, not a reference manual

Structure serves flow. A subsection earns its number when the argument shifts topic, not when a new formal object is named. Target three to four subsections per top-level section. The v1 Paper 2 has 32 h2 subsections under 10 h1 sections — that is a manual layout, not an argument layout.

### Thread the central claim — develop, don't restate

Each LENS paper has one claim that is the reason the paper exists. Paper 1: a single decomposition of perceived quality explains six unrelated-looking selection phenomena and gives you design principles. Paper 2: architecture beats individual ability, and platforms beat elite VCs because of architecture, not because of access. Paper 3: an LLM, prompted via instruction distillation, ranks startup pitches in alignment with a 10-expert crowd at NDCG@20 = 0.923.

The abstract introduces the claim. The results section demonstrates it. The discussion names its significance. The conclusion closes on it. Each appearance adds something the previous one didn't — this is building, not restating. Test: remove any one appearance. Does the reader lose something they cannot get from the others? If yes, it earns its place.

### Honest accounting goes in one place

State what the paper does not claim, state the falsification conditions, state the limitations — once, at the end, clearly. Mid-argument self-interruption ("we acknowledge this is observational data and N is small") deflates the argument without adding epistemic value if the same caveat appears two pages later.

### Cite the neighborhood

Every concept the paper borrows needs the foundational reference in the bibliography. If you invoke the winner's curse, cite Capen, Clapp & Campbell (1971) and Thaler (1988). If you invoke homophily, cite McPherson, Smith-Lovin & Cook (2001). If you invoke order statistics, cite a textbook. If you invoke wisdom of crowds, cite Galton (1907) and Surowiecki (2004). A reviewer who knows the adjacent literature notices what is missing before they notice what is present. Aim for 15–25 references in a focused paper, more if the paper bridges two literatures.

### Numbers from one model do not travel to another

The simulation in Paper 2 produces specific numbers (3.91% platform quality, 3.51% elite VC quality). The empirical study in Paper 3 produces specific numbers (NDCG@10 = 0.908). These are *not* directly comparable. The v1 papers occasionally drop numbers from one paper into the prose of another with the same precision. State the relationship; do not import the magnitude.

### The reader has what the reader has

Never reference a document the reader cannot access. "The original results table" is meaningless if the reader does not have the table. Either reproduce the necessary content or cut the reference. The v1 papers point at internal CSVs without telling the reader what is in them.

---

## The Author's Voice

The papers are not blog posts and they are not committee documents. They are written by a specific person watching a specific phenomenon carefully. The reader should be able to feel that.

### Show how you think, not how you feel

Not memoir. The author does not share feelings about venture capital or personal investment outcomes. What comes through is a way of seeing — the habit of noticing what *the architecture* of a process is doing to the outputs, not what the participants believe they are doing. The opening case in Paper 1 works (or should work) because the reader can feel someone watching carefully: "the winning VC celebrates internally; two years later they realize they paid 40% above fair value." That is a person observing a pattern, not a framework outputting one.

### Dry humor earns trust, used sparingly

"The committee grew from three members to twelve. The variance went down. The bias did not." That kind of line — short, factual, slightly resigned — does more for credibility than three paragraphs of careful hedging. It shows the author can see the absurdity in the framework's implication, including for the practices people are proud of. Use sparingly. One or two per paper. Never in the abstract. Place where the framework produces an uncomfortable conclusion.

### Self-implication

The LENS framework predicts that any selection process — including peer review of this paper — is subject to the dynamics it describes. The author is a participant in selection systems, not an observer of them. A line acknowledging that the paper itself was produced through processes the framework critiques is not a rhetorical flourish; it is the framework applied to itself. Place it where it has maximum force, usually at the end of the conclusion.

### No contempt

The framework critiques the architecture, not the people inside it. The hiring manager whose committee produces a homogeneous team is not the villain. The VC who lost money on the deal they "won" is not stupid. The point is that intelligent, well-intentioned actors operating intelligently and in good faith inside an architecture with the structural properties LENS describes will produce the patterns LENS describes. Contempt would require standing outside the architecture; the framework says nobody stands outside.

### Conditional, not totalizing

"Multi-stage architectures with diverse evaluator biases consistently outperform single-stage architectures with homogeneous biases on selection quality, scale, and consistency in the configurations we simulate" is the defensible claim. Not: "platforms are the future of all selection." The paper is strongest when it stays structural, conditional, mechanism-oriented. Every sentence that sounds like a manifesto is a sentence a reviewer will attack rather than engage.

### Not academic, but not casual

Sentences build and accumulate. They should not require a second read to get the point. The blog voice uses short punchy sentences with gaps. The paper voice uses longer sentences that build, but each one still says one thing. The difference is rhythm, not clarity. Both are clear. The paper breathes more slowly.

---

## Formatting

- **Headings.** Numbered Arabic. `## 4. Results`. `### 4.1 Subsection Name`. No bold wrap on headings. No `#### Phenomenon 1: ...` h4 chains; if you need that depth you have over-subdivided.
- **Inline math.** Single `$...$`. `q̂ = q + βᵀx + ε` written as `$\hat q = q + \beta^\top x + \varepsilon$` if the paper goes through pandoc to LaTeX, or as plain Unicode if it stays Markdown for arXiv.
- **Display math.** Double `$$...$$` only for the central decomposition equation and the two or three theorem statements that anchor the paper.
- **Tables.** Only for parameter lists and multi-condition result summaries. Three columns or fewer if at all possible. Caption above; one-line legend below if needed.
- **Bullet lists.** Reserve for genuine disjunction (a list of three intervention types, a list of two model providers). Do not use for "three reasons why X" or "five implications" — those should be prose.
- **Citations.** Author-year inline ("Galton, 1907"); single-citation form for direct support, multi-citation when chaining ("Brooks et al., 2014; Pollack et al., 2012"). Bibliography at the end, alphabetical by first author.
- **References to code and data.** Use Markdown link form: `[code/paper3_llm_eval/aggregate_ndcg.py](code/paper3_llm_eval/aggregate_ndcg.py)`. The reader following the paper on GitHub gets a clickable cross-reference.
- **Section count.** Eight to ten top-level sections. More than eleven signals structural bloat (Paper 2 v1 had ten with a missing §7).

---

## The Acid Test

After writing any paragraph, three checks:

1. **Can a smart non-specialist get the point on first read?** If not, lead with the human version.
2. **Does this paragraph say exactly one thing?** If two, split it.
3. **Is this the only place in the paper this point is made?** If not, keep the best version and cut the rest.

A fourth check, specific to the LENS rewrites:

4. **Could this paragraph be a bullet list?** If yes, you have not finished writing it.
