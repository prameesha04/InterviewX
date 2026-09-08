"""
Interview Question Generation Agent

Generates personalized interview questions using RAG.
Questions are tailored to the candidate's profile, target role, and identified skill gaps.
Produces a mix of technical, behavioral, and HR questions.
"""

import json
import re
from rag.retriever import retrieve_as_text
from llm.watsonx_client import generate_text

QUESTION_TYPES = {
    "technical": "technical_questions.txt",
    "behavioral": "behavioral_questions.txt",
    "hr": "hr_questions.txt",
    "role_specific": "role_specific.txt",
}

SYSTEM_CONTEXT = """You are a senior technical interviewer designing a personalized interview 
session for a candidate. You craft questions that are specific, challenging at the right level, 
and directly relevant to the candidate's background and target role."""


def generate_question_set(profile: dict, analysis: dict, count: int = 8) -> list:
    """
    Generate a full set of interview questions for the session.

    Args:
        profile: Candidate profile dict
        analysis: Profile analysis result dict (from profile_agent)
        count: Total number of questions to generate

    Returns:
        List of question dicts: [{id, question, type, difficulty, topic}, ...]
    """
    # Distribute questions across types
    distribution = _get_distribution(count)
    all_questions = []
    question_id = 1

    for q_type, q_count in distribution.items():
        questions = _generate_questions_for_type(
            profile=profile,
            analysis=analysis,
            q_type=q_type,
            count=q_count,
            start_id=question_id,
        )
        all_questions.extend(questions)
        question_id += len(questions)

    return all_questions


def generate_single_question(
    profile: dict,
    analysis: dict,
    q_type: str,
    asked_questions: list = None,
) -> dict:
    """
    Generate one fresh question of the given type, avoiding repeats.

    Args:
        profile: Candidate profile dict
        analysis: Profile analysis result dict
        q_type: One of "technical", "behavioral", "hr"
        asked_questions: List of previously asked question strings (to avoid repeats)

    Returns:
        Single question dict: {id, question, type, difficulty, topic}
    """
    asked_questions = asked_questions or []
    questions = _generate_questions_for_type(
        profile=profile,
        analysis=analysis,
        q_type=q_type,
        count=1,
        start_id=len(asked_questions) + 1,
        avoid=asked_questions,
    )
    if questions:
        return questions[0]
    return _fallback_question(q_type, len(asked_questions) + 1)


def _get_distribution(total: int) -> dict:
    """Distribute questions across types. Heavier on technical."""
    technical = max(1, round(total * 0.5))
    behavioral = max(1, round(total * 0.3))
    hr = total - technical - behavioral
    return {"technical": technical, "behavioral": behavioral, "hr": hr}


def _generate_questions_for_type(
    profile: dict,
    analysis: dict,
    q_type: str,
    count: int,
    start_id: int,
    avoid: list = None,
) -> list:
    """Generate `count` questions of a specific type using RAG context."""
    avoid = avoid or []

    # Build RAG context from the knowledge base
    rag_query = _build_rag_query(profile, analysis, q_type)
    source_file = QUESTION_TYPES.get(q_type)
    context = retrieve_as_text(rag_query, k=5, source_filter=source_file)

    prompt = _build_prompt(profile, analysis, q_type, count, context, avoid)
    raw_output = generate_text(prompt, max_new_tokens=400, temperature=0.75)
    questions = _parse_questions(raw_output, q_type, start_id)

    if len(questions) < count:
        questions.extend([
            _fallback_question(q_type, start_id + i)
            for i in range(count - len(questions))
        ])

    return questions[:count]


def _build_rag_query(profile: dict, analysis: dict, q_type: str) -> str:
    target_role = profile.get("target_role", "software engineer")
    skills = profile.get("skills", "")
    gaps = ", ".join(analysis.get("skill_gaps", []))
    return f"{q_type} interview questions for {target_role} role, skills: {skills}, gaps: {gaps}"


def _build_prompt(
    profile: dict,
    analysis: dict,
    q_type: str,
    count: int,
    context: str,
    avoid: list,
) -> str:
    avoid_block = ""
    if avoid:
        avoid_list = "\n".join(f"- {q}" for q in avoid[:5])
        avoid_block = f"\n\nDO NOT repeat these already-asked questions:\n{avoid_list}"

    level_guidance = {
        "fresher": "beginner to intermediate difficulty, focus on fundamentals and concepts",
        "junior": "intermediate difficulty, mix of concepts and practical application",
        "mid": "intermediate to advanced, focus on design and problem-solving",
        "senior": "advanced difficulty, focus on architecture, leadership, and complex trade-offs",
    }
    difficulty_hint = level_guidance.get(
        profile.get("skill_level", "fresher"),
        "appropriate difficulty for the candidate's level"
    )

    type_guidance = {
        "technical": f"technical questions about {profile.get('skills', 'relevant technologies')} "
                     f"and core concepts for a {profile.get('target_role', 'developer')} role",
        "behavioral": "behavioral questions using the STAR method format, focused on teamwork, "
                      "leadership, problem-solving, and growth",
        "hr": "HR and motivational questions about career goals, strengths/weaknesses, "
              "company fit, and self-introduction",
    }

    return f"""You are a senior interviewer generating personalized {q_type} interview questions.

CANDIDATE PROFILE:
- Target Role: {profile.get('target_role', 'Software Engineer')}
- Skills: {profile.get('skills', 'Not specified')}
- Experience: {profile.get('experience', 'Not specified')}
- Skill Level: {profile.get('skill_level', 'fresher')}
- Key Skill Gaps Identified: {', '.join(analysis.get('skill_gaps', []))}
- Focus Areas: {', '.join(analysis.get('focus_areas', []))}

RELEVANT KNOWLEDGE BASE CONTEXT:
{context if context else 'Use your expertise to generate relevant questions.'}

TASK: Generate exactly {count} {type_guidance.get(q_type, q_type)} questions.
Difficulty: {difficulty_hint}.
{avoid_block}

Output ONLY a valid JSON array with no extra text. Format:
[
  {{
    "question": "<the full interview question>",
    "type": "{q_type}",
    "difficulty": "<easy|medium|hard>",
    "topic": "<brief topic label e.g. 'Data Structures', 'Teamwork', 'Career Goals'>"
  }}
]

Generate exactly {count} questions now:"""


def _parse_questions(raw: str, q_type: str, start_id: int) -> list:
    """Extract JSON array of questions from LLM output."""
    json_match = re.search(r'\[.*\]', raw, re.DOTALL)
    if json_match:
        try:
            items = json.loads(json_match.group())
            result = []
            for i, item in enumerate(items):
                if isinstance(item, dict) and "question" in item:
                    result.append({
                        "id": start_id + i,
                        "question": item["question"].strip(),
                        "type": item.get("type", q_type),
                        "difficulty": item.get("difficulty", "medium"),
                        "topic": item.get("topic", q_type.capitalize()),
                    })
            return result
        except (json.JSONDecodeError, ValueError):
            pass
    return []


def _fallback_question(q_type: str, question_id: int) -> dict:
    fallbacks = {
        "technical": {
            "question": "Explain the difference between a stack and a queue, and give a real-world use case for each.",
            "topic": "Data Structures",
            "difficulty": "medium",
        },
        "behavioral": {
            "question": "Tell me about a time you had to work under pressure to meet a deadline. What was the outcome?",
            "topic": "Time Management",
            "difficulty": "medium",
        },
        "hr": {
            "question": "Tell me about yourself and why you are interested in this role.",
            "topic": "Self Introduction",
            "difficulty": "easy",
        },
    }
    fb = fallbacks.get(q_type, fallbacks["technical"])
    return {"id": question_id, "type": q_type, **fb}
