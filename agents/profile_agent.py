"""
Profile Analysis Agent

Analyzes the candidate's profile (skills, education, experience, target role)
and returns a structured analysis: strengths, skill gaps, readiness level,
and recommended focus areas for the interview session.
"""

import json
import re
from llm.watsonx_client import generate_text


SYSTEM_CONTEXT = """You are an expert technical recruiter and career coach with 15 years of experience 
evaluating candidates for technology roles. You analyze candidate profiles objectively and provide 
honest, constructive assessments."""


def analyze_profile(profile: dict) -> dict:
    """
    Analyze the candidate profile and return a structured assessment.

    Args:
        profile: dict with keys:
            - name (str)
            - education (str)
            - skills (str) — comma-separated or free text
            - experience (str) — description of work/project experience
            - target_role (str)
            - skill_level (str) — "fresher", "junior", "mid", "senior"

    Returns:
        dict with keys: strengths, skill_gaps, readiness_score, focus_areas, summary
    """
    prompt = _build_prompt(profile)
    raw_output = generate_text(prompt, max_new_tokens=900, temperature=0.4)
    return _parse_response(raw_output, profile)


def _build_prompt(profile: dict) -> str:
    return f"""{SYSTEM_CONTEXT}

Analyze the following candidate profile and provide a structured assessment for interview preparation.

CANDIDATE PROFILE:
- Name: {profile.get('name', 'Candidate')}
- Education: {profile.get('education', 'Not specified')}
- Skills: {profile.get('skills', 'Not specified')}
- Experience: {profile.get('experience', 'Not specified')}
- Target Role: {profile.get('target_role', 'Not specified')}
- Skill Level: {profile.get('skill_level', 'fresher')}

Provide your analysis in the following JSON format ONLY. Do not include any text before or after the JSON:

{{
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "skill_gaps": ["gap 1", "gap 2", "gap 3"],
  "readiness_score": <integer 1-10>,
  "focus_areas": ["area 1", "area 2", "area 3"],
  "summary": "<2-3 sentence overall assessment of the candidate>"
}}

Rules:
- strengths: List 3-5 specific strengths based on their profile
- skill_gaps: List 3-5 specific gaps between their current skills and target role requirements
- readiness_score: Integer from 1-10 representing interview readiness (1=not ready, 10=very ready)
- focus_areas: List 3-4 specific topics they should focus on in this interview session
- summary: Concise overall assessment

Respond with valid JSON only:"""


def _parse_response(raw: str, profile: dict) -> dict:
    """Parse the LLM JSON response, with a fallback if parsing fails."""
    # Extract JSON block from the response
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            # Validate required keys
            required = ["strengths", "skill_gaps", "readiness_score", "focus_areas", "summary"]
            if all(k in data for k in required):
                # Ensure readiness_score is an int in range
                data["readiness_score"] = max(1, min(10, int(data.get("readiness_score", 5))))
                return data
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: return a minimal structure so the app can continue
    return {
        "strengths": [
            f"Background in {profile.get('education', 'relevant field')}",
            f"Interest in {profile.get('target_role', 'technology')}",
            "Motivated to improve through structured practice",
        ],
        "skill_gaps": [
            "Analysis could not be fully completed — please retry",
            f"Review core competencies for {profile.get('target_role', 'target role')}",
        ],
        "readiness_score": 5,
        "focus_areas": [
            "Technical fundamentals",
            "Behavioral questions using STAR method",
            "Role-specific knowledge",
        ],
        "summary": (
            f"Profile analysis for {profile.get('name', 'the candidate')} targeting "
            f"{profile.get('target_role', 'the selected role')} was processed. "
            "Proceed with the interview session for a detailed assessment."
        ),
    }
