"""
Interview Evaluation Agent

Evaluates a candidate's answer to an interview question.
Provides:
  - Score out of 10
  - Strengths of the answer
  - Weaknesses / areas for improvement
  - A model / improved answer
  - Specific recommendations
"""

import json
import re
from rag.retriever import retrieve_as_text
from llm.watsonx_client import generate_text

SYSTEM_CONTEXT = """You are an expert interview coach and technical evaluator with deep expertise 
in evaluating interview answers across technical, behavioral, and HR domains. 
You provide fair, constructive, and specific feedback to help candidates improve."""


def evaluate_answer(
    question: dict,
    answer: str,
    profile: dict,
    analysis: dict,
) -> dict:
    """
    Evaluate a candidate's answer to an interview question.

    Args:
        question: Question dict {id, question, type, difficulty, topic}
        answer: The candidate's answer text
        profile: Candidate profile dict
        analysis: Profile analysis dict (for context on level and gaps)

    Returns:
        dict with keys:
            score (int 0-10), strengths (list), weaknesses (list),
            model_answer (str), recommendations (list), overall_comment (str)
    """
    # Retrieve evaluation guidelines and relevant context via RAG
    eval_context = retrieve_as_text(
        f"evaluation guidelines for {question.get('type', 'technical')} interview answers",
        k=3,
        source_filter="evaluation_guidelines.txt",
    )

    prompt = _build_prompt(question, answer, profile, analysis, eval_context)
    raw_output = generate_text(prompt, max_new_tokens=1100, temperature=0.3)
    return _parse_response(raw_output, question, answer, profile)


def _build_prompt(
    question: dict,
    answer: str,
    profile: dict,
    analysis: dict,
    eval_context: str,
) -> str:
    skill_level = profile.get("skill_level", "fresher")
    target_role = profile.get("target_role", "Software Engineer")
    q_type = question.get("type", "technical")
    q_text = question.get("question", "")

    level_note = {
        "fresher": "This is a fresh graduate or entry-level candidate. Evaluate accordingly — reward strong conceptual understanding even without extensive work experience.",
        "junior": "This is a junior-level candidate with 1-2 years of experience. Expect basic practical application.",
        "mid": "This is a mid-level candidate. Expect solid practical knowledge and examples.",
        "senior": "This is a senior-level candidate. Expect in-depth knowledge, trade-off analysis, and architectural thinking.",
    }.get(skill_level, "Evaluate at an appropriate level for the candidate.")

    return f"""{SYSTEM_CONTEXT}

EVALUATION CONTEXT FROM KNOWLEDGE BASE:
{eval_context if eval_context else 'Use your expertise to evaluate the answer.'}

CANDIDATE CONTEXT:
- Name: {profile.get('name', 'Candidate')}
- Target Role: {target_role}
- Skill Level: {skill_level}
- {level_note}

INTERVIEW QUESTION ({q_type.upper()} | {question.get('difficulty', 'medium').upper()} | Topic: {question.get('topic', 'General')}):
"{q_text}"

CANDIDATE'S ANSWER:
"{answer if answer.strip() else '[No answer provided]'}"

TASK: Evaluate this answer thoroughly and respond ONLY with valid JSON in the exact format below:

{{
  "score": <integer 0-10>,
  "strengths": ["specific strength 1", "specific strength 2"],
  "weaknesses": ["specific weakness or gap 1", "specific weakness 2"],
  "model_answer": "<a complete, well-structured model answer to this question that the candidate can learn from>",
  "recommendations": ["specific actionable recommendation 1", "specific actionable recommendation 2", "specific actionable recommendation 3"],
  "overall_comment": "<1-2 sentence honest overall assessment of the answer>"
}}

Scoring guide:
- 9-10: Excellent — accurate, detailed, well-structured, includes examples and trade-offs
- 7-8: Good — correct with minor gaps, clear structure
- 5-6: Adequate — partially correct, missing depth or examples  
- 3-4: Needs improvement — mostly incorrect or very shallow
- 1-2: Poor — significant errors, very incomplete
- 0: No answer or completely off-topic

Be honest, specific, and constructive. Do not be harsh but do not inflate scores.
Respond with valid JSON only:"""


def _parse_response(raw: str, question: dict, answer: str, profile: dict) -> dict:
    """Parse the LLM evaluation JSON, with a fallback if parsing fails."""
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            required = ["score", "strengths", "weaknesses", "model_answer", "recommendations", "overall_comment"]
            if all(k in data for k in required):
                data["score"] = max(0, min(10, int(data["score"])))
                # Ensure lists are actually lists
                for list_key in ["strengths", "weaknesses", "recommendations"]:
                    if not isinstance(data[list_key], list):
                        data[list_key] = [str(data[list_key])]
                return data
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # Fallback evaluation
    return {
        "score": 5,
        "strengths": [
            "An answer was provided for the question",
            "Shows willingness to engage with the topic",
        ],
        "weaknesses": [
            "The evaluation could not be fully processed — please try again",
            "Consider providing more structured and detailed responses",
        ],
        "model_answer": (
            f"A strong answer to '{question.get('question', 'this question')}' would "
            f"demonstrate clear understanding of the concept, include a concrete example, "
            f"and discuss relevant trade-offs or alternatives."
        ),
        "recommendations": [
            "Structure your answers clearly with an introduction, main points, and conclusion",
            "Always include a concrete example from your projects or studies",
            f"Review core concepts relevant to {profile.get('target_role', 'your target role')}",
        ],
        "overall_comment": (
            "Evaluation encountered an issue. Please retry for a detailed assessment."
        ),
    }


def compute_session_summary(evaluations: list) -> dict:
    """
    Compute aggregate session statistics from a list of evaluation dicts.

    Returns:
        dict with: average_score, total_questions, passed (>=6), failed (<6),
                   top_strengths, top_weaknesses, overall_recommendations
    """
    if not evaluations:
        return {}

    scores = [e.get("score", 0) for e in evaluations]
    avg = round(sum(scores) / len(scores), 1)

    all_strengths = []
    all_weaknesses = []
    all_recommendations = []

    for e in evaluations:
        all_strengths.extend(e.get("strengths", []))
        all_weaknesses.extend(e.get("weaknesses", []))
        all_recommendations.extend(e.get("recommendations", []))

    return {
        "average_score": avg,
        "total_questions": len(evaluations),
        "passed": sum(1 for s in scores if s >= 6),
        "failed": sum(1 for s in scores if s < 6),
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "top_strengths": list(dict.fromkeys(all_strengths))[:4],
        "top_weaknesses": list(dict.fromkeys(all_weaknesses))[:4],
        "overall_recommendations": list(dict.fromkeys(all_recommendations))[:5],
        "performance_level": _performance_label(avg),
    }


def _performance_label(avg: float) -> str:
    if avg >= 8.5:
        return "Outstanding"
    if avg >= 7.0:
        return "Strong"
    if avg >= 5.5:
        return "Satisfactory"
    if avg >= 4.0:
        return "Needs Improvement"
    return "Significant Work Required"
