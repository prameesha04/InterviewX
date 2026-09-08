"""
InterviewX – Flask Application
AI-Powered Personalized Interview Trainer

Routes:
  GET  /                   → Dashboard / home
  GET  /profile            → Candidate profile form
  POST /profile/analyze    → Analyze profile (AJAX)
  GET  /interview          → Interview session page
  POST /interview/start    → Start a new session
  POST /interview/answer   → Submit an answer (AJAX)
  POST /interview/next     → Get next question (AJAX)
  GET  /results/<session_id> → Session results page
  GET  /history            → All session history
  POST /history/clear      → Clear history
  GET  /api/status         → Health check
"""

import os
import uuid
import json
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")

# ---------------------------------------------------------------------------
# In-memory session store (keyed by session_id)
# In a production deployment this would be replaced by Redis or a database.
# ---------------------------------------------------------------------------
_sessions: dict = {}


# ---------------------------------------------------------------------------
# Lazy-initialise agents so the app starts fast even before the vector store
# is fully loaded.
# ---------------------------------------------------------------------------
def _get_profile_agent():
    from agents.profile_agent import analyze_profile
    return analyze_profile


def _get_question_agent():
    from agents.question_agent import generate_question_set, generate_single_question
    return generate_question_set, generate_single_question


def _get_evaluation_agent():
    from agents.evaluation_agent import evaluate_answer, compute_session_summary
    return evaluate_answer, compute_session_summary


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def _make_session_id() -> str:
    return str(uuid.uuid4())[:8].upper()


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _get_or_init_history() -> list:
    if "history" not in session:
        session["history"] = []
    return session["history"]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    history = _get_or_init_history()
    return render_template("index.html", history=history)


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/profile/analyze", methods=["POST"])
def analyze_profile_route():
    data = request.get_json(force=True)
    required = ["name", "target_role", "skill_level"]
    for field in required:
        if not data.get(field, "").strip():
            return jsonify({"error": f"Field '{field}' is required."}), 400

    profile_data = {
        "name": data.get("name", "").strip(),
        "education": data.get("education", "").strip(),
        "skills": data.get("skills", "").strip(),
        "experience": data.get("experience", "").strip(),
        "target_role": data.get("target_role", "").strip(),
        "skill_level": data.get("skill_level", "fresher"),
    }

    try:
        analyze_profile = _get_profile_agent()
        analysis = analyze_profile(profile_data)
    except EnvironmentError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        app.logger.error(f"Profile analysis error: {e}")
        return jsonify({"error": "Profile analysis failed. Please check your watsonx.ai credentials."}), 500

    # Store in Flask session for the interview flow
    session["profile"] = profile_data
    session["analysis"] = analysis
    session.modified = True

    return jsonify({"analysis": analysis, "profile": profile_data})


@app.route("/interview")
def interview():
    if "profile" not in session:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("profile"))
    return render_template(
        "interview.html",
        profile=session["profile"],
        analysis=session["analysis"],
    )


@app.route("/interview/start", methods=["POST"])
def start_interview():
    if "profile" not in session:
        return jsonify({"error": "Profile not found. Please complete your profile first."}), 400

    data = request.get_json(force=True)
    num_questions = int(data.get("num_questions", 8))
    num_questions = max(3, min(15, num_questions))

    profile = session["profile"]
    analysis = session["analysis"]

    try:
        generate_question_set, _ = _get_question_agent()
        questions = generate_question_set(profile, analysis, count=num_questions)
    except EnvironmentError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        app.logger.error(f"Question generation error: {e}")
        return jsonify({"error": "Question generation failed. Please check your watsonx.ai credentials."}), 500

    session_id = _make_session_id()
    _sessions[session_id] = {
        "id": session_id,
        "profile": profile,
        "analysis": analysis,
        "questions": questions,
        "current_index": 0,
        "answers": [],
        "evaluations": [],
        "started_at": _now(),
        "completed": False,
    }

    session["active_session_id"] = session_id
    session.modified = True

    first_question = questions[0] if questions else None
    return jsonify({
        "session_id": session_id,
        "total_questions": len(questions),
        "question": first_question,
    })


@app.route("/interview/answer", methods=["POST"])
def submit_answer():
    session_id = session.get("active_session_id")
    if not session_id or session_id not in _sessions:
        return jsonify({"error": "No active session found. Please start a new interview."}), 400

    data = request.get_json(force=True)
    answer_text = data.get("answer", "").strip()

    if not answer_text:
        return jsonify({"error": "Answer cannot be empty."}), 400

    sess = _sessions[session_id]
    current_idx = sess["current_index"]

    if current_idx >= len(sess["questions"]):
        return jsonify({"error": "All questions have been answered."}), 400

    question = sess["questions"][current_idx]
    profile = sess["profile"]
    analysis = sess["analysis"]

    try:
        evaluate_answer, _ = _get_evaluation_agent()
        evaluation = evaluate_answer(question, answer_text, profile, analysis)
    except EnvironmentError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        app.logger.error(f"Evaluation error: {e}")
        return jsonify({"error": "Evaluation failed. Please check your watsonx.ai credentials."}), 500

    sess["answers"].append({
        "question_id": question["id"],
        "question": question["question"],
        "type": question.get("type", "technical"),
        "difficulty": question.get("difficulty", "medium"),
        "topic": question.get("topic", ""),
        "answer": answer_text,
        "timestamp": _now(),
    })
    sess["evaluations"].append(evaluation)
    sess["current_index"] += 1

    # Check if session is complete
    is_complete = sess["current_index"] >= len(sess["questions"])
    if is_complete:
        _, compute_session_summary = _get_evaluation_agent()
        sess["summary"] = compute_session_summary(sess["evaluations"])
        sess["completed"] = True
        sess["completed_at"] = _now()

        # Persist to history in Flask session
        history = _get_or_init_history()
        history.insert(0, {
            "session_id": session_id,
            "profile_name": profile.get("name", "Candidate"),
            "target_role": profile.get("target_role", ""),
            "skill_level": profile.get("skill_level", ""),
            "date": _now(),
            "total_questions": len(sess["questions"]),
            "average_score": sess["summary"].get("average_score", 0),
            "performance_level": sess["summary"].get("performance_level", ""),
            "completed": True,
        })
        # Keep last 20 sessions in history
        session["history"] = history[:20]
        session.modified = True

    return jsonify({
        "evaluation": evaluation,
        "question_index": current_idx,
        "is_complete": is_complete,
        "session_id": session_id,
    })


@app.route("/interview/next", methods=["POST"])
def next_question():
    session_id = session.get("active_session_id")
    if not session_id or session_id not in _sessions:
        return jsonify({"error": "No active session found."}), 400

    sess = _sessions[session_id]
    current_idx = sess["current_index"]

    if current_idx >= len(sess["questions"]):
        return jsonify({"done": True, "session_id": session_id})

    question = sess["questions"][current_idx]
    return jsonify({
        "question": question,
        "question_number": current_idx + 1,
        "total_questions": len(sess["questions"]),
        "done": False,
    })


@app.route("/results/<session_id>")
def results(session_id):
    sess = _sessions.get(session_id)
    if not sess:
        flash("Session not found or expired.", "warning")
        return redirect(url_for("index"))

    qa_pairs = []
    for i, ans in enumerate(sess["answers"]):
        qa_pairs.append({
            "question": ans,
            "evaluation": sess["evaluations"][i] if i < len(sess["evaluations"]) else {},
        })

    return render_template(
        "results.html",
        sess=sess,
        qa_pairs=qa_pairs,
        summary=sess.get("summary", {}),
    )


@app.route("/history")
def history():
    history_list = _get_or_init_history()
    return render_template("history.html", history=history_list)


@app.route("/history/clear", methods=["POST"])
def clear_history():
    session["history"] = []
    session.modified = True
    flash("Session history cleared.", "info")
    return redirect(url_for("history"))


@app.route("/api/status")
def api_status():
    """Health check endpoint — verifies environment configuration."""
    checks = {
        "flask": "ok",
        "watsonx_api_key": "set" if os.getenv("WATSONX_API_KEY") else "missing",
        "watsonx_project_id": "set" if os.getenv("WATSONX_PROJECT_ID") else "missing",
        "watsonx_url": os.getenv("WATSONX_URL", "not set"),
    }
    all_ok = all(v not in ("missing",) for v in checks.values())
    return jsonify({
        "status": "ready" if all_ok else "configuration_required",
        "checks": checks,
        "timestamp": _now(),
    })


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("base.html"), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
