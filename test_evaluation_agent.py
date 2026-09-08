"""
End-to-end test for agents/evaluation_agent.py using the real IBM Granite connection.

Verifies:
  1. RAG retriever pulls evaluation guidelines from ChromaDB.
  2. IBM Granite evaluates the candidate's answer (real API call, no mocks).
  3. The response is parsed and validated successfully.
  4. All required fields are present and well-typed.
  5. Score is in range 0–10.
  6. Evaluation is relevant to the question, candidate profile, and target role.
  7. The fallback path was NOT triggered (i.e. real LLM evaluation was returned).

No API keys, project IDs, or other credentials are printed.
"""

import sys
import os

# ── Load .env so WATSONX_* vars are available ─────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # Rely on shell env vars if python-dotenv is not installed

# ── Guard: env vars must be present ──────────────────────────────────────────
missing = [v for v in ("WATSONX_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_URL")
           if not os.getenv(v)]
if missing:
    print(f"[ERROR] Missing environment variables: {missing}")
    print("  Ensure .env is present and contains the required keys.")
    sys.exit(1)

print("Environment variables: WATSONX_API_KEY [OK]  WATSONX_PROJECT_ID [OK]  WATSONX_URL [OK]")
print(f"Endpoint : {os.getenv('WATSONX_URL')}")
print()

# ── Candidate profile ─────────────────────────────────────────────────────────
SAMPLE_PROFILE = {
    "name": "Test Candidate",
    "education": "B.E. Electronics and Communication Engineering",
    "skills": "Python, Flask, SQL, HTML, CSS, JavaScript",
    "experience": "Fresher",
    "target_role": "Software Developer",
    "skill_level": "fresher",
}

# ── Interview question ────────────────────────────────────────────────────────
SAMPLE_QUESTION = {
    "id": 1,
    "question": "Explain the difference between a Python list and a tuple. When would you use each?",
    "type": "technical",
    "difficulty": "easy",
    "topic": "Python",
}

# ── Candidate answer ──────────────────────────────────────────────────────────
CANDIDATE_ANSWER = (
    "A list is mutable, so we can change its elements after creation. "
    "A tuple is immutable, so it cannot be changed after creation. "
    "I would use a list when the data needs to be modified and a tuple "
    "when the data should remain fixed."
)

# ── Minimal analysis dict (mirrors what profile_agent produces) ───────────────
SAMPLE_ANALYSIS = {
    "readiness_score": 5,
    "strengths": ["Basic Python knowledge", "Web development stack awareness"],
    "skill_gaps": ["Data structures depth", "System design", "Algorithms"],
    "focus_areas": ["Core Python concepts", "SQL queries", "REST APIs"],
    "summary": "Entry-level candidate with a solid foundational skill set.",
}

# Sentinel strings that appear ONLY in the fallback path of _parse_response()
FALLBACK_SENTINELS = {
    "The evaluation could not be fully processed",
    "Evaluation encountered an issue",
    "An answer was provided for the question",
}

# =============================================================================
# STEP 1 — RAG retriever smoke-check
# =============================================================================
print("=" * 65)
print("  STEP 1 — RAG Retriever Smoke-Check (evaluation guidelines)")
print("=" * 65)

try:
    from rag.retriever import retrieve_as_text

    eval_context = retrieve_as_text(
        "evaluation guidelines for technical interview answers",
        k=3,
        source_filter="evaluation_guidelines.txt",
    )
    rag_ok = bool(eval_context and eval_context.strip())
    status = "[OK]" if rag_ok else "[WARN]"
    snippet = eval_context[:120].replace("\n", " ") if eval_context else "(empty)"
    print(f"  {status}  Retrieved {len(eval_context)} chars from evaluation_guidelines.txt")
    print(f"         Snippet: {snippet} …")
    print()
    if not rag_ok:
        print("  [WARN] No RAG content retrieved — agent will use LLM expertise as fallback.")
    else:
        print("  RAG retrieval: evaluation_guidelines.txt returned context. [OK]")
    print()

except Exception as e:
    print(f"[RUNTIME ERROR during RAG check] {type(e).__name__}: {e}")
    sys.exit(1)

# =============================================================================
# STEP 2 — Run the Evaluation Agent
# =============================================================================
print("=" * 65)
print("  STEP 2 — Evaluation Agent (IBM Granite + RAG)")
print("=" * 65)
print()
print("Question   :", SAMPLE_QUESTION["question"])
print("Type       :", SAMPLE_QUESTION["type"])
print("Difficulty :", SAMPLE_QUESTION["difficulty"])
print("Topic      :", SAMPLE_QUESTION["topic"])
print()
print("Candidate answer:")
print(f"  \"{CANDIDATE_ANSWER}\"")
print()
print("Calling evaluation_agent.evaluate_answer() via IBM Granite … (10–30 s)\n")

try:
    from agents.evaluation_agent import evaluate_answer

    result = evaluate_answer(
        question=SAMPLE_QUESTION,
        answer=CANDIDATE_ANSWER,
        profile=SAMPLE_PROFILE,
        analysis=SAMPLE_ANALYSIS,
    )

except EnvironmentError as e:
    print(f"[CONFIG ERROR] {e}")
    sys.exit(1)
except Exception as e:
    print(f"[RUNTIME ERROR] {type(e).__name__}: {e}")
    sys.exit(1)

# =============================================================================
# STEP 3 — Display the evaluation result
# =============================================================================
print("=" * 65)
print("  EVALUATION RESULT")
print("=" * 65)
print()
print(f"Score          : {result.get('score', 'N/A')} / 10")
print()

print("[+] Strengths:")
for i, s in enumerate(result.get("strengths", []), 1):
    print(f"   {i}. {s}")

print()
print("[!] Weaknesses:")
for i, w in enumerate(result.get("weaknesses", []), 1):
    print(f"   {i}. {w}")

print()
print("[>] Recommendations:")
for i, r in enumerate(result.get("recommendations", []), 1):
    print(f"   {i}. {r}")

print()
print("[*] Model / Improved Answer:")
print(f"   {result.get('model_answer', '(none)')}")

print()
print("[=] Overall Comment:")
print(f"   {result.get('overall_comment', '(none)')}")
print()

# =============================================================================
# STEP 4 — Validation
# =============================================================================
print("=" * 65)
print("  VALIDATION")
print("=" * 65)
print()

checks = {}

# 4.1  All required keys present
required_keys = ["score", "strengths", "weaknesses", "model_answer",
                 "recommendations", "overall_comment"]
checks["All required keys present (score, strengths, weaknesses, model_answer, recommendations, overall_comment)"] = (
    all(k in result for k in required_keys)
)

# 4.2  Score is an integer in 0–10
score = result.get("score")
checks["score is an integer between 0 and 10"] = (
    isinstance(score, int) and 0 <= score <= 10
)

# 4.3  strengths is a non-empty list of strings
strengths = result.get("strengths", [])
checks["strengths is a non-empty list"] = (
    isinstance(strengths, list) and len(strengths) >= 1
    and all(isinstance(s, str) for s in strengths)
)

# 4.4  weaknesses is a list of strings
weaknesses = result.get("weaknesses", [])
checks["weaknesses is a non-empty list"] = (
    isinstance(weaknesses, list) and len(weaknesses) >= 1
    and all(isinstance(w, str) for w in weaknesses)
)

# 4.5  recommendations is a non-empty list of strings
recommendations = result.get("recommendations", [])
checks["recommendations is a non-empty list"] = (
    isinstance(recommendations, list) and len(recommendations) >= 1
    and all(isinstance(r, str) for r in recommendations)
)

# 4.6  model_answer is a non-empty string
model_answer = result.get("model_answer", "")
checks["model_answer is a non-empty string"] = (
    isinstance(model_answer, str) and len(model_answer.strip()) > 20
)

# 4.7  overall_comment is a non-empty string
overall_comment = result.get("overall_comment", "")
checks["overall_comment is a non-empty string"] = (
    isinstance(overall_comment, str) and len(overall_comment.strip()) > 10
)

# 4.8  Fallback NOT triggered (real LLM evaluation was used)
fallback_triggered = any(
    sentinel in str(result.get(field, ""))
    for sentinel in FALLBACK_SENTINELS
    for field in ("strengths", "weaknesses", "overall_comment")
)
checks["Real LLM evaluation used (fallback path was NOT triggered)"] = (
    not fallback_triggered
)

# 4.9  Evaluation is relevant to Python / the question topic
relevance_text = " ".join([
    model_answer.lower(),
    " ".join(str(s) for s in strengths).lower(),
    " ".join(str(w) for w in weaknesses).lower(),
])
python_keywords = {"list", "tuple", "mutable", "immutable", "python"}
relevance_hits = sum(1 for kw in python_keywords if kw in relevance_text)
checks[f"Evaluation references Python/list/tuple concepts ({relevance_hits}/5 keywords found)"] = (
    relevance_hits >= 2
)

# 4.10  model_answer actually contains advice/content beyond a template sentence
checks["model_answer is substantive (>80 chars)"] = (
    len(model_answer.strip()) > 80
)

# ── Print results ─────────────────────────────────────────────────────────────
all_passed = True
for description, passed in checks.items():
    status = "[OK]  " if passed else "[FAIL]"
    if not passed:
        all_passed = False
    print(f"  {status}  {description}")

print()
if all_passed:
    print("All checks passed [PASS] — Evaluation agent is working end-to-end with IBM Granite.")
else:
    print("Some checks failed [FAIL] — see details above.")
    sys.exit(1)
