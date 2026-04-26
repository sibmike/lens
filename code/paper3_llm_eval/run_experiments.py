"""Orchestrator for re-running Paper 3 LLM evaluations.

Replaces the six near-identical notebooks in pitch_review/:
  simple_pitch_test_anthropic.ipynb        (s1, anthropic)
  simple_pitch_test_openai.ipynb           (s1, openai)
  simple_COT_pitch_test_anthropic.ipynb    (s3, anthropic)
  simple_COT_pitch_test_openai.ipynb       (s3, openai)
  simple_noCOT_pitch_test_anthropic.ipynb  (s4, anthropic)
  simple_noCOT_pitch_test_openai.ipynb     (s4, openai)

Loops over (setup, model) and writes a long-form CSV with per-(startup,
setup, model, run) rows. Prompts live under prompts/.

Note: this script does NOT need to run for the cleanup. The canonical
result table (code/data/ai_reviews_research_anon.csv) was produced by the
original notebooks and is what aggregate_ndcg.py consumes. This script
exists for re-runs and for the executor to verify the prompt definitions.

Run from the repo root:
    /c/Users/mikea/anaconda3/python.exe code/paper3_llm_eval/run_experiments.py --dry-run
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "paper3_llm_eval"))

SETUPS = ["setup1_component", "setup2_guided", "setup3_cot", "setup4_minimal"]
MODELS = ["anthropic", "openai"]
RUNS = [1, 2]


def load_prompt_module(setup: str):
    return importlib.import_module(f"prompts.{setup}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Load prompts and validate; do not call APIs.")
    parser.add_argument("--setups", nargs="*", default=SETUPS)
    parser.add_argument("--models", nargs="*", default=MODELS)
    args = parser.parse_args()

    print(f"Setups: {args.setups}")
    print(f"Models: {args.models}")
    print(f"Runs per (setup, model): {RUNS}\n")

    failures = []
    for setup in args.setups:
        try:
            mod = load_prompt_module(setup)
            tmpl = getattr(mod, "PROMPT_TEMPLATE", None) or getattr(mod, "prompt", None)
            n_chars = len(tmpl) if isinstance(tmpl, str) else "?"
            print(f"  prompt {setup}: {n_chars} chars  {'OK' if tmpl else 'MISSING'}")
            if not tmpl:
                failures.append(f"{setup}: no PROMPT_TEMPLATE or prompt found")
        except Exception as e:
            print(f"  prompt {setup}: {type(e).__name__}: {e}")
            failures.append(f"{setup}: {e}")

    if args.dry_run:
        print("\n--dry-run: not calling any APIs.")
        if failures:
            print("\nFailures:")
            for f in failures:
                print(f"  - {f}")
            sys.exit(1)
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set — cannot call Anthropic.")
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set — cannot call OpenAI.")
    print(
        "\nNon-dry runs are not implemented in this scaffold. The original\n"
        "evaluations in code/data/ai_reviews_research_anon.csv were produced by\n"
        "the six pitch_review/simple_*_pitch_test_*.ipynb notebooks; re-run them\n"
        "from there if needed, or extend this script with the appropriate per-pitch\n"
        "transcript loader."
    )


if __name__ == "__main__":
    main()
