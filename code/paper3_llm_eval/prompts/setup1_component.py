"""Setup 1 — Component-based evaluation (4 criteria, structured JSON output).

This is the prompt used by the canonical PitchReviewSystem in
code/paper3_llm_eval/pitch_evaluator.py: evaluate one criterion at a time
(market_potential, solution_viability, team_capability, initial_traction)
with the methodology guideline as system context. The four criterion scores
are then averaged into the final score.

Setup 1 is the best-performing single configuration in Paper 3 (NDCG@10 = 0.908
with the Anthropic model).

The actual prompt construction is in PitchReviewSystem._build_evaluation_prompt;
this module exists so run_experiments.py can dispatch by setup name.
"""

from pitch_evaluator import METHODOLOGY  # type: ignore[import-not-found]

PROMPT_TEMPLATE = (
    "[Setup 1: component-based]\n"
    "Methodology context (passed as system instruction):\n"
    f"{METHODOLOGY}\n\n"
    "Per-criterion prompt is constructed at runtime by "
    "PitchReviewSystem._build_evaluation_prompt(pitch_transcript, criteria_name, criteria_questions)."
)
