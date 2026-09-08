# InterviewX – AI-Powered Personalized Interview Trainer

An AI-powered interview preparation platform for students and entry-level candidates, built with Python/Flask and IBM Granite through IBM watsonx.ai.

---

## Architecture

```
Candidate Profile → Profile Analysis Agent → Question Generation Agent (RAG) → Candidate Answer → Evaluation Agent → Feedback Dashboard
```

### AI Agents

| Agent | Responsibility |
|---|---|
| **Profile Analysis Agent** | Analyzes skills, education, experience, target role; identifies strengths and gaps |
| **Question Generation Agent** | Generates personalized technical/behavioral/HR questions via RAG |
| **Interview Evaluation Agent** | Scores answers (0–10), identifies strengths/weaknesses, provides model answers |

---

## Project Structure

```
InterviewX/
├── app.py                      # Flask application entry point
├── requirements.txt
├── .env.example                # Environment variable template
├── README.md
├── agents/
│   ├── __init__.py
│   ├── profile_agent.py        # Profile Analysis Agent
│   ├── question_agent.py       # Question Generation Agent
│   └── evaluation_agent.py     # Interview Evaluation Agent
├── rag/
│   ├── __init__.py
│   ├── loader.py               # Knowledge base loader & vector store builder
│   └── retriever.py            # RAG retriever
├── llm/
│   ├── __init__.py
│   └── watsonx_client.py       # IBM watsonx.ai / Granite LLM client
├── knowledge_base/
│   ├── technical_questions.txt
│   ├── behavioral_questions.txt
│   ├── hr_questions.txt
│   ├── role_specific.txt
│   └── evaluation_guidelines.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── profile.html
│   ├── interview.html
│   └── history.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- IBM Cloud account with watsonx.ai service
- IBM Cloud API key

### 1. Clone the repository

```bash
git clone <repo-url>
cd InterviewX
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=your-random-secret-key
```

### 5. Build the knowledge base (vector store)

```bash
python -c "from rag.loader import build_vector_store; build_vector_store()"
```

### 6. Run the application

```bash
python app.py
```

Open your browser at `http://localhost:5000`.

---

## IBM watsonx.ai Configuration

- **Model**: `ibm/granite-13b-instruct-v2` (configurable)
- **API**: IBM watsonx.ai Runtime REST API
- **Authentication**: IAM API key via `ibm-watsonx-ai` SDK

Obtain credentials from:
- API Key: https://cloud.ibm.com/iam/apikeys
- Project ID: watsonx.ai → your project → Manage → General

---

## Key Features

- **Profile Analysis**: AI analyzes your background and identifies skill gaps before the interview
- **Personalized Questions**: RAG-powered question generation tailored to your profile and target role
- **Live Evaluation**: Real-time AI scoring and feedback on every answer
- **Session History**: Review past sessions, scores, and improvement over time
- **Clean Dashboard**: Responsive UI with score breakdowns and recommendations

---

## Future Scope

- Resume PDF parsing
- Voice-to-text answer submission
- Multilingual support
- Mock video interview mode
- LinkedIn profile import

---

## License

MIT
