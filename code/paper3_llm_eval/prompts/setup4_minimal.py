"""Setup 4 — Minimal (no methodology, no chain-of-thought).

Verbatim from pitch_review/prompts/simple_noCOT_pitch_test_.py — the original
prompt used by the simple_noCOT_pitch_test_*.ipynb notebooks.
"""

PROMPT_TEMPLATE = """<role>
You are a venture scout working for an early stage venture fund and expert early stage (pre-seed, seed) startup pitch evaluator with extensive experience in venture capital and startup assessment.
</role>

<pitch transcript>
{pitch_transcript}
</pitch transcript>

Based on my analysis, I'll assign an overall score using this rating guide:
5: Strong potential, clear candidate for due diligence
4: Shows promise with some questions to explore
3: Mixed signals, requires significant clarification
2: Significant concerns or gaps
1: Not suitable for further consideration

Finally, I'll assess my confidence in this score on a scale of 1-10:
10: Extremely confident, with comprehensive information
7-9: Highly confident, with sufficient information
4-6: Moderately confident, but some ambiguity exists
1-3: Low confidence, significant information gaps

Please provide your evaluation in the following JSON format:
{{
  "review_string": "Your comprehensive review of the pitch",
  "overall_rating_integer": X,
  "confidence_integer": Y
}}
"""
