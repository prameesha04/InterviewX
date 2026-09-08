"""
End-to-end test for agents/profile_agent.py using the real IBM Granite connection.
No credentials are printed; only the structured analysis result is shown.
"""

import sys
import os
import json

# ── Load .env so WATSONX_* vars are available ─────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # If python-dotenv not installed, rely on shell env vars

# ── Sample candidate profile ──────────────────────────────────────────────────
SAMPLE_PROFILE = {
    "name": "Test Candidate",
    "education": "B.E. Electronics and Communication Engineering",
    "skills": "Python, Flask, SQL, HTML, CSS, JavaScript",
    "experience": "Fresher",
    "target_role": "Software Developer",
    "skill_level": "Entry-level",
}

# ── Sanity-check: env vars present (without printing values) ──────────────────
missing = [v for v in ("WATSONX_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_URL")
           if not os.getenv(v)]
if missing:
    print(f"[ERROR] Missing environment variables: {missing}")
    print("  Ensure .env is present and contains the required keys.")
    sys.exit(1)

print("Environment variables: WATSONX_API_KEY [OK]  WATSONX_PROJECT_ID [OK]  WATSONX_URL [OK]")
print(f"Endpoint : {os.getenv('WATSONX_URL')}")
print()

# ── Run the agent ─────────────────────────────────────────────────────────────
print("=" * 60)
print("  Profile Analysis Agent — End-to-End Test")
print("=" * 60)
print("\nCandidate profile submitted:")
for k, v in SAMPLE_PROFILE.items():
    print(f"  {k:15s}: {v}")
print()

try:
    from agents.profile_agent import analyze_profile

    print("Sending profile to IBM Granite via watsonx_client … (this may take 10–30 s)\n")
    result = analyze_profile(SAMPLE_PROFILE)

except EnvironmentError as e:
    print(f"[CONFIG ERROR] {e}")
    sys.exit(1)
except Exception as e:
    print(f"[RUNTIME ERROR] {type(e).__name__}: {e}")
    sys.exit(1)

# ── Display results ────────────────────────────────────────────────────────────
print("=" * 60)
print("  ANALYSIS RESULT")
print("=" * 60)

strengths = result.get("strengths", [])
skill_gaps = result.get("skill_gaps", [])
readiness_score = result.get("readiness_score", "N/A")
focus_areas = result.get("focus_areas", [])
summary = result.get("summary", "")

print(f"\nReadiness Score : {readiness_score} / 10")

print("\n[+] Candidate Strengths:")
for i, s in enumerate(strengths, 1):
    print(f"   {i}. {s}")

print("\n[!] Skill Gaps:")
for i, g in enumerate(skill_gaps, 1):
    print(f"   {i}. {g}")

print("\n[>] Focus Areas (Recommendations):")
for i, f in enumerate(focus_areas, 1):
    print(f"   {i}. {f}")

print(f"\nSummary:\n   {summary}")

# ── Validate structure ────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  VALIDATION")
print("=" * 60)

required_keys = ["strengths", "skill_gaps", "readiness_score", "focus_areas", "summary"]
all_ok = True

for key in required_keys:
    present = key in result and result[key] not in (None, [], "")
    status = "[OK]" if present else "[FAIL]"
    if not present:
        all_ok = False
    print(f"  {status}  {key}")

score = result.get("readiness_score")
score_ok = isinstance(score, int) and 1 <= score <= 10
score_status = "[OK]" if score_ok else "[FAIL]"
if not score_ok:
    all_ok = False
print(f"  {score_status}  readiness_score in range 1-10")

print()
if all_ok:
    print("All checks passed [PASS] -- Profile agent is working end-to-end with IBM Granite.")
else:
    print("Some checks failed [FAIL] -- see details above.")
    sys.exit(1)
