"""Setup 2 — Guided methodology (single-pass with full methodology in prompt)."""

from pitch_evaluator import METHODOLOGY  # type: ignore[import-not-found]

PROMPT_TEMPLATE = f"""<role>
You are an expert venture capital evaluator. Use the methodology below to score
the pitch transcript on a 1-5 scale.
</role>

<methodology>
{METHODOLOGY}
</methodology>

<pitch_transcript>
{{pitch_transcript}}
</pitch_transcript>

Provide your evaluation as JSON:
{{{{
  "review_string": "Comprehensive review",
  "overall_rating_integer": 1-5,
  "confidence_integer": 1-10
}}}}
"""
