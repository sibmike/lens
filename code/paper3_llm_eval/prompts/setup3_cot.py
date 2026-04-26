"""Setup 3 — Chain-of-thought (explicit reasoning before scoring).

NOTE: Setup 3 data is missing from code/data/ai_reviews_research_anon.csv.
Paper 3 §3 lists 4 setups; only s1, s2, s4 are present in the canonical
results table. The v2 paper editor must either re-run Setup 3 or correct
the prose to 3 setups.
"""

PROMPT_TEMPLATE = """<role>
You are an expert venture capital evaluator. Reason step by step before
assigning a score.
</role>

<pitch_transcript>
{pitch_transcript}
</pitch_transcript>

<chain_of_thought>
Walk through the following questions explicitly before scoring:
  1. What is the market opportunity, and how large is it?
  2. Is the solution viable and differentiated?
  3. Does the team have the right expertise?
  4. What traction signals are present?
  5. What are the strongest and weakest aspects of the pitch?

Then assign a score using:
  5: Strong potential, clear due-diligence candidate
  4: Promising with open questions
  3: Mixed signals
  2: Significant concerns
  1: Not suitable
</chain_of_thought>

Output JSON:
{{
  "reasoning": "Step-by-step analysis",
  "review_string": "Final review",
  "overall_rating_integer": 1-5,
  "confidence_integer": 1-10
}}
"""
