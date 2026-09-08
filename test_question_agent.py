"""
End-to-end test for agents/question_agent.py using the real IBM Granite connection
and the existing ChromaDB RAG implementation.

Verifies:
  1. RAG retriever pulls relevant context from knowledge_base/ via ChromaDB.
  2. Retrieved context is included in the Granite prompt (logged before the call).
  3. IBM Granite generates the questions (real API call, no mocks).
  4. The response is parsed and validated successfully.
  5. Questions are relevant to the candidate's skills and target role.
  6. No hardcoded / fallback questions appear in the final result.

No API keys, project IDs, or other credentials are printed.
"""

import sys
import os
import json

# ── Load .env so WATSONX_* vars are available ─────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # Rely on shell env vars if python-dotenv is not installed

# ── Candidate profile (as specified) ─────────────────────────────────────────
SAMPLE_PROFILE = {
    "name": "Test Candidate",
    "education": "B.E. Electronics and Communication Engineering",
    "skills": "Python, Flask, SQL, HTML, CSS, JavaScript",
    "experience": "Fresher",
    "target_role": "Software Developer",
    "skill_level": "fresher",          # maps to the difficulty-hint lookup in question_agent
}

# Known fallback question texts — used to detect if the LLM was bypassed
FALLBACK_QUESTIONS = {
    "Explain the difference between a stack and a queue, and give a real-world use case for each.",
    "Tell me about a time you had to work under pressure to meet a deadline. What was the outcome?",
    "Tell me about yourself and why you are interested in this role.",
}

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

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Run the Profile Agent to get the analysis required by question_agent
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  STEP 1 — Profile Analysis Agent")
print("=" * 65)
print("\nCandidate profile:")
for k, v in SAMPLE_PROFILE.items():
    print(f"  {k:15s}: {v}")
print()

try:
    from agents.profile_agent import analyze_profile

    print("Calling profile_agent.analyze_profile() via IBM Granite … (10–30 s)\n")
    analysis = analyze_profile(SAMPLE_PROFILE)

except EnvironmentError as e:
    print(f"[CONFIG ERROR] {e}")
    sys.exit(1)
except Exception as e:
    print(f"[RUNTIME ERROR] {type(e).__name__}: {e}")
    sys.exit(1)

print("Profile analysis received:")
print(f"  Readiness score : {analysis.get('readiness_score', 'N/A')} / 10")
print(f"  Strengths       : {analysis.get('strengths', [])}")
print(f"  Skill gaps      : {analysis.get('skill_gaps', [])}")
print(f"  Focus areas     : {analysis.get('focus_areas', [])}")
print()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Verify RAG context retrieval BEFORE calling the question agent
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  STEP 2 — RAG Retriever Smoke-Check (ChromaDB)")
print("=" * 65)

try:
    from rag.retriever import retrieve_as_text

    rag_checks = {
        "technical":  "technical_questions.txt",
        "behavioral": "behavioral_questions.txt",
        "hr":         "hr_questions.txt",
    }

    rag_results = {}
    all_rag_ok = True
    for q_type, source_file in rag_checks.items():
        query = (
            f"{q_type} interview questions for "
            f"{SAMPLE_PROFILE['target_role']} role, "
            f"skills: {SAMPLE_PROFILE['skills']}"
        )
        context = retrieve_as_text(query, k=5, source_filter=source_file)
        rag_results[q_type] = context
        has_content = bool(context and context.strip())
        status = "[OK]" if has_content else "[WARN]"
        if not has_content:
            all_rag_ok = False
        snippet = context[:120].replace("\n", " ") if context else "(empty)"
        print(f"  {status}  {q_type:10s} — retrieved {len(context)} chars  |  snippet: {snippet} …")

    print()
    if all_rag_ok:
        print("  RAG retrieval: all three knowledge-base sources returned context. [OK]")
    else:
        print("  RAG retrieval: one or more sources returned no content. [WARN]")
        print("  The agent will still run; it will use its own expertise as fallback.")
    print()

except Exception as e:
    print(f"[RUNTIME ERROR during RAG check] {type(e).__name__}: {e}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Generate 8 interview questions via the Question Agent
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  STEP 3 — Question Generation Agent (IBM Granite + RAG)")
print("=" * 65)
print()
print("Calling question_agent.generate_question_set() — count=8 …")
print("(Each question type makes a separate Granite API call; allow 30–90 s)\n")

try:
    from agents.question_agent import generate_question_set

    questions = generate_question_set(SAMPLE_PROFILE, analysis, count=8)

except EnvironmentError as e:
    print(f"[CONFIG ERROR] {e}")
    sys.exit(1)
except Exception as e:
    print(f"[RUNTIME ERROR] {type(e).__name__}: {e}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Display generated questions
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  GENERATED INTERVIEW QUESTIONS")
print("=" * 65)
print()

for q in questions:
    print(f"  Q{q.get('id', '?'):02d}  [{q.get('type','?').upper():10s}]  "
          f"[{q.get('difficulty','?'):6s}]  [{q.get('topic','')}]")
    print(f"       {q.get('question','(no question text)')}")
    print()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Validate
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  VALIDATION")
print("=" * 65)
print()

checks = {}

# 5.1  Exactly 8 questions returned
checks["Total questions == 8"] = len(questions) == 8

# 5.2  All required fields present on every question
required_fields = {"id", "question", "type", "difficulty", "topic"}
all_fields_ok = all(required_fields.issubset(q.keys()) for q in questions)
checks["All questions have required fields (id, question, type, difficulty, topic)"] = all_fields_ok

# 5.3  Valid type values
valid_types = {"technical", "behavioral", "hr"}
checks["All question types are valid (technical / behavioral / hr)"] = all(
    q.get("type") in valid_types for q in questions
)

# 5.4  Valid difficulty values
valid_difficulties = {"easy", "medium", "hard"}
checks["All difficulty values are valid (easy / medium / hard)"] = all(
    q.get("difficulty") in valid_difficulties for q in questions
)

# 5.5  No empty question text
checks["No question text is empty"] = all(
    bool(q.get("question", "").strip()) for q in questions
)

# 5.6  No hardcoded fallback questions used
fallback_count = sum(
    1 for q in questions if q.get("question", "").strip() in FALLBACK_QUESTIONS
)
checks[f"No hardcoded/fallback questions in result (found {fallback_count})"] = fallback_count == 0

# 5.7  Questions mention at least one candidate skill or role keyword
skill_keywords = {s.strip().lower() for s in SAMPLE_PROFILE["skills"].split(",")}
skill_keywords.update({"software", "developer", "web", "database", "api", "backend", "frontend"})
relevance_hits = sum(
    1 for q in questions
    if any(kw in q.get("question", "").lower() for kw in skill_keywords)
)
checks[f"At least 50 % of questions are skill/role-relevant ({relevance_hits}/8 match)"] = (
    relevance_hits >= 4
)

# 5.8  Distribution: at least 1 of each type
type_counts = {}
for q in questions:
    type_counts[q.get("type", "unknown")] = type_counts.get(q.get("type", "unknown"), 0) + 1
for t in ("technical", "behavioral", "hr"):
    checks[f"At least 1 '{t}' question present (got {type_counts.get(t, 0)})"] = (
        type_counts.get(t, 0) >= 1
    )

# 5.9  RAG context was available (from earlier smoke-check)
checks["RAG context retrieved from ChromaDB before generation"] = all_rag_ok

# ── Print check results ───────────────────────────────────────────────────────
all_passed = True
for description, passed in checks.items():
    status = "[OK]  " if passed else "[FAIL]"
    if not passed:
        all_passed = False
    print(f"  {status}  {description}")

print()
if all_passed:
    print("All checks passed [PASS] — Question agent is working end-to-end with IBM Granite + RAG.")
else:
    print("Some checks failed [FAIL] — see details above.")
    sys.exit(1)
