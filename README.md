# InterviewX – AI-Powered Personalized Interview Trainer

InterviewX is an AI-powered personalized interview preparation platform designed for students and entry-level candidates.

The system analyzes a candidate's profile, generates personalized interview questions using Retrieval-Augmented Generation (RAG), evaluates candidate answers, identifies skill gaps, and provides actionable recommendations using **IBM Granite through IBM watsonx.ai Runtime**.

---

## 🎯 Project Objective

The objective of InterviewX is to provide an intelligent and personalized interview training experience.

Instead of asking the same generic questions to every candidate, InterviewX considers:

- Candidate education
- Technical skills
- Experience level
- Target job role
- Skill level
- Interview category
- Previous answers and performance

The platform then dynamically generates questions and evaluates responses using IBM Granite.

---

## 🚀 Key Features

### 1. Candidate Profile Analysis

The Profile Analysis Agent analyzes:

- Education
- Technical skills
- Experience
- Target job role
- Skill level

It identifies:

- Candidate strengths
- Skill gaps
- Interview readiness
- Areas that require improvement
- Personalized recommendations

### 2. Personalized Interview Question Generation

The Question Generation Agent generates interview questions based on the candidate's profile.

It supports:

- Technical questions
- Behavioral questions
- HR questions
- Role-specific questions

Questions are generated dynamically using IBM Granite instead of hardcoded AI responses.

### 3. Retrieval-Augmented Generation (RAG)

InterviewX uses RAG to provide relevant interview knowledge to the Granite model before generating questions or evaluating answers.

The knowledge base contains:

- Technical interview questions
- Behavioral interview questions
- HR questions
- Role-specific interview knowledge
- Interview evaluation guidelines

The retrieved context helps the AI generate more relevant and context-aware responses.

### 4. AI-Powered Answer Evaluation

The Evaluation Agent evaluates the candidate's answer using IBM Granite.

The evaluation provides:

- Score out of 10
- Strengths
- Weaknesses
- Areas for improvement
- Improved/model answer
- Personalized recommendations
- Overall feedback

### 5. Skill Gap Identification

InterviewX analyzes candidate performance and identifies areas where the candidate needs improvement.

For example:

- Python fundamentals
- SQL
- Flask
- Communication
- Problem solving
- Behavioral responses

### 6. Interview Session

The platform provides an interactive interview experience.

The candidate:

1. Creates a profile
2. Starts an interview
3. Receives one question at a time
4. Submits an answer
5. Receives AI evaluation
6. Proceeds to the next question
7. Completes the interview
8. Views the final performance summary

### 7. Performance Results

After completing an interview session, InterviewX displays:

- Question-by-question scores
- Technical performance
- Behavioral performance
- HR performance
- Strengths
- Weaknesses
- Recommendations
- Overall interview performance

---

## 🧠 Agentic AI Architecture

InterviewX uses three specialized AI agents.

```text
                     Candidate Profile
                            |
                            v
               +-------------------------+
               | Profile Analysis Agent  |
               +-------------------------+
                            |
                     Profile Insights
                            |
                            v
               +-------------------------+
               | Question Generation     |
               | Agent                   |
               +-------------------------+
                            |
                     RAG Knowledge Base
                            |
                            v
                  Personalized Questions
                            |
                            v
                     Candidate Answer
                            |
                            v
               +-------------------------+
               | Interview Evaluation    |
               | Agent                   |
               +-------------------------+
                            |
                            v
                  Score + Feedback + Gaps
                            |
                            v
                    Recommendations
```

---

## 🤖 AI Agents

### Profile Analysis Agent

**Purpose:** Understand the candidate.

**Responsibilities:**

- Analyze candidate profile
- Identify strengths
- Identify skill gaps
- Determine interview readiness
- Generate personalized recommendations

### Interview Question Generation Agent

**Purpose:** Generate personalized interview questions.

**Responsibilities:**

- Understand candidate profile
- Understand target job role
- Retrieve relevant knowledge using RAG
- Generate technical questions
- Generate behavioral questions
- Generate HR questions
- Adapt questions to candidate skill level

### Interview Evaluation Agent

**Purpose:** Evaluate candidate responses.

**Responsibilities:**

- Analyze candidate answer
- Assign score out of 10
- Identify strengths
- Identify weaknesses
- Generate improved/model answer
- Recommend improvements
- Identify skill gaps

---

## 🔎 RAG Architecture

InterviewX uses Retrieval-Augmented Generation to provide relevant interview knowledge to IBM Granite.

```text
Knowledge Base
      |
      v
Document Loader
      |
      v
Text Chunking
      |
      v
Embeddings
      |
      v
ChromaDB Vector Store
      |
      v
Relevant Context Retrieval
      |
      v
IBM Granite
      |
      v
AI Generated Response
```

The knowledge base is divided into different areas:

```text
knowledge_base/
│
├── technical_questions.txt
├── behavioral_questions.txt
├── hr_questions.txt
├── role_specific.txt
└── evaluation_guidelines.txt
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend and AI integration |
| Flask | Web application backend |
| HTML | Frontend structure |
| CSS | User interface styling |
| JavaScript | Frontend interactions |
| IBM Granite | Generative AI model |
| IBM watsonx.ai Runtime | AI model inference |
| IBM Cloud | Cloud AI infrastructure |
| RAG | Context-aware AI generation |
| ChromaDB | Vector database |
| LangChain | RAG pipeline |
| Hugging Face Embeddings | Document embeddings |

---

## ☁️ IBM Technologies

### IBM Granite

InterviewX currently uses:

```text
ibm/granite-4-h-small
```

IBM Granite is used for:

- Profile analysis
- Question generation
- Answer evaluation
- Feedback generation
- Personalized recommendations

### IBM watsonx.ai Runtime

The Granite model is accessed through IBM watsonx.ai Runtime.

The application communicates with the IBM service using:

- IBM Cloud API authentication
- watsonx.ai Runtime
- Project ID
- Granite model endpoint

### IBM Bob

IBM Bob is used as the AI-assisted development environment for building and modifying the InterviewX application.

It assists with:

- Project structure
- Code generation
- Debugging
- Dependency management
- Integration
- Testing

---

## 📁 Project Structure

```text
InterviewX/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── agents/
│   ├── profile_agent.py
│   ├── question_agent.py
│   └── evaluation_agent.py
│
├── rag/
│   ├── loader.py
│   └── retriever.py
│
├── llm/
│   └── watsonx_client.py
│
├── knowledge_base/
│   ├── technical_questions.txt
│   ├── behavioral_questions.txt
│   ├── hr_questions.txt
│   ├── role_specific.txt
│   └── evaluation_guidelines.txt
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── profile.html
│   ├── interview.html
│   ├── results.html
│   └── history.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

---

## ⚙️ Prerequisites

Before running InterviewX, install:

- Python 3.14
- pip
- IBM Cloud account
- IBM watsonx.ai Runtime service
- IBM Cloud API Key
- IBM watsonx.ai project

---

## 🔐 Environment Configuration

InterviewX uses environment variables to protect credentials.

Create a local `.env` file:

```env
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

Do not commit the `.env` file to GitHub.

Never hardcode API keys inside Python source files.

---

## 📦 Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Navigate into the project:

```bash
cd InterviewX
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🗃️ Build the RAG Knowledge Base

InterviewX uses ChromaDB as the vector store.

The knowledge base documents are stored inside:

```text
knowledge_base/
```

The RAG pipeline:

1. Loads interview documents
2. Splits documents into chunks
3. Generates embeddings
4. Stores embeddings in ChromaDB
5. Retrieves relevant context during interview generation/evaluation

The local vector database is stored in:

```text
chroma_db/
```

The ChromaDB directory is ignored by Git and can be recreated locally.

---

## ▶️ Running the Application

Start the Flask application:

```bash
python app.py
```

The application will run locally at:

```text
http://127.0.0.1:5000
```

Open the URL in your browser.

---

## 🔄 End-to-End Workflow

```text
START
  |
  v
Candidate Profile
  |
  v
Profile Analysis Agent
  |
  v
Strengths + Skill Gaps
  |
  v
Question Generation Agent
  |
  v
RAG Knowledge Retrieval
  |
  v
IBM Granite Generation
  |
  v
Personalized Questions
  |
  v
Candidate Answer
  |
  v
Evaluation Agent
  |
  v
IBM Granite Evaluation
  |
  +--> Score
  +--> Strengths
  +--> Weaknesses
  +--> Model Answer
  +--> Recommendations
  |
  v
Skill Gap Analysis
  |
  v
Final Performance Report
  |
  v
END
```

---

## 💬 Example Interview Flow

### Candidate Profile

```text
Education:
B.E. Electronics and Communication Engineering

Skills:
Python, Flask, SQL, HTML, CSS, JavaScript

Experience:
Fresher

Target Role:
Software Developer

Skill Level:
Entry Level
```

### Generated Technical Question

**Example:**

```text
Explain the difference between a Python list and a tuple.
When would you use each?
```

The question is generated dynamically based on the candidate profile and retrieved interview context.

### Candidate Answer

The candidate submits their response through the InterviewX interface.

### AI Evaluation

The Evaluation Agent generates:

```text
Score: 6/10

Strengths:
- Correctly explained mutability.
- Correctly identified common use cases.

Weaknesses:
- Limited discussion of performance.
- Did not provide practical examples.
- Could explain memory considerations in more depth.

Recommendations:
- Include real-world examples.
- Explain when immutability is useful.
- Compare performance and memory characteristics.
```

The exact evaluation is generated dynamically by IBM Granite.

---

## 📊 Performance Dashboard

The final results page provides a summary of the interview.

### Performance Categories

- Technical Performance
- Behavioral Performance
- HR Performance
- Overall Performance

The system also provides question-level analysis.

### Example

| Question | Score |
|---|---:|
| Question 1 | 5/10 |
| Question 2 | 7/10 |
| Question 3 | 8/10 |
| Question 4 | 6/10 |
| Question 5 | 6/10 |
| Question 6 | 7/10 |
| Question 7 | 7/10 |
| Question 8 | 7/10 |

These scores are generated from actual candidate responses through the Evaluation Agent.

---

## 🧩 Agent Interaction

The three agents work together as a coordinated workflow.

```text
Profile Agent
      |
      | Candidate understanding
      v
Question Agent
      |
      | Personalized questions
      v
Candidate
      |
      | Answer
      v
Evaluation Agent
      |
      | Feedback + Skill gaps
      v
Personalized Recommendations
```

This agent-based approach separates responsibilities and makes the application easier to extend.

---

## 🧠 Model Configuration

InterviewX currently uses:

```text
Model:
ibm/granite-4-h-small

IBM Service:
watsonx.ai Runtime

Region:
Dallas / us-south

API:
IBM watsonx.ai Runtime Chat API
```

The application uses the IBM watsonx.ai SDK to communicate with the Granite model.

---

## 🔒 Security

InterviewX follows basic credential protection practices.

Sensitive information is stored using environment variables.

The following files/directories should not be committed:

```text
.env
.env.example
chroma_db/
__pycache__/
venv/
.venv/
```

The `.gitignore` file prevents these files from being added to Git.

### Important

Never upload the following to GitHub or public repositories:

- IBM API keys
- Access tokens
- Bearer tokens
- Passwords
- Private credentials

If a credential is accidentally exposed, revoke or rotate it immediately.

---

## 🧪 Validation & Testing

InterviewX was tested at multiple levels.

### Profile Analysis Agent

The Profile Analysis Agent was tested using a sample entry-level Software Developer profile.

Validation included:

- Profile parsing
- Strength identification
- Skill gap identification
- Readiness score
- Recommendations
- Granite response generation

### Question Generation Agent

The Question Generation Agent was tested with:

- Technical questions
- Behavioral questions
- HR questions
- RAG retrieval
- IBM Granite generation

The RAG system successfully retrieved relevant interview context from the knowledge base.

### Evaluation Agent

The Evaluation Agent was tested using candidate answers.

The system successfully generated:

- Score
- Strengths
- Weaknesses
- Recommendations
- Model answer
- Overall feedback

### End-to-End Testing

The complete browser workflow was tested:

```text
Profile
   ↓
AI Profile Analysis
   ↓
Start Interview
   ↓
Question Generation
   ↓
Candidate Answer
   ↓
AI Evaluation
   ↓
Next Question
   ↓
Final Results
```

The complete interview session was successfully executed through the Flask web application.

---

## 💡 Novelty

InterviewX provides several features that distinguish it from a traditional static interview-question platform.

### 1. Profile-Based Personalization

Questions are generated according to the candidate's:

- Skills
- Education
- Experience
- Target role
- Skill level

### 2. Context-Aware Question Generation

RAG retrieves relevant interview knowledge before generating questions.

This improves contextual relevance.

### 3. Multi-Agent AI Workflow

Different AI agents are responsible for different stages:

```text
Profile Analysis
       ↓
Question Generation
       ↓
Answer Evaluation
```

This provides a modular agent-based architecture.

### 4. Intelligent Feedback Loop

The candidate does not simply receive a score.

The system explains:

- What was done well
- What was missing
- How the answer can be improved
- What the candidate should study next

### 5. Skill Gap Identification

Performance is used to identify areas requiring further preparation.

### 6. End-to-End Interview Preparation

InterviewX combines:

```text
Profile Analysis
      +
Question Generation
      +
Interview Practice
      +
AI Evaluation
      +
Skill Gap Analysis
      +
Recommendations
```

into one platform.

---

## 🌱 Future Scope

InterviewX can be extended with several advanced capabilities.

### Resume Parsing

Automatically extract:

- Education
- Skills
- Projects
- Experience
- Certifications

from a candidate resume.

### Job Description Analysis

The system could analyze a job description and identify:

- Required skills
- Preferred skills
- Technologies
- Experience requirements

Questions could then be generated specifically for that job description.

### Voice-Based Interviews

Future versions can support:

- Speech-to-text
- Voice questions
- Voice answers
- Communication analysis
- Pronunciation analysis

### Multilingual Interview Training

The system can support multiple languages for candidates who prefer regional-language interview preparation.

### Real-Time Interview Analytics

Future versions could provide:

- Response time
- Answer quality trends
- Topic-wise performance
- Skill progression
- Interview readiness score

### Company-Specific RAG

The RAG knowledge base can be expanded with:

- Company interview experiences
- Company-specific technical topics
- Job-specific interview patterns
- Role-specific preparation material

### Adaptive Difficulty

The interview difficulty can automatically change based on candidate performance.

For example:

```text
Good Answer
     ↓
Increase Difficulty
     ↓
Advanced Question
```

or:

```text
Weak Answer
     ↓
Reduce Difficulty
     ↓
Fundamental Question
```

### Personalized Preparation Roadmap

Based on identified skill gaps, InterviewX could generate a personalized preparation plan.

**Example:**

```text
Week 1
Python Fundamentals

Week 2
SQL + Database Concepts

Week 3
Flask + REST APIs

Week 4
Mock Interviews
```

---

## 📌 Project Highlights

- ✔ IBM Granite Integration
- ✔ IBM watsonx.ai Runtime
- ✔ IBM Cloud
- ✔ IBM Bob
- ✔ Multi-Agent Architecture
- ✔ Retrieval-Augmented Generation
- ✔ ChromaDB Vector Store
- ✔ Personalized Interview Questions
- ✔ AI Answer Evaluation
- ✔ Skill Gap Identification
- ✔ Personalized Recommendations
- ✔ Flask Web Application
- ✔ Responsive Dashboard

---

## 📚 Project Domain

**Domain:** Education / Career Development

**Project:** InterviewX – AI-Powered Personalized Interview Trainer

---

## 👨‍💻 Development Environment

InterviewX was developed using:

- Python
- Flask
- HTML
- CSS
- JavaScript
- IBM Bob
- IBM watsonx.ai
- IBM Granite
- LangChain
- ChromaDB

---

## 📜 License

This project is intended for educational and demonstration purposes.

A suitable open-source license can be added when publishing the final repository.

---

## 🙏 Acknowledgement

This project was developed as part of an IBM internship/project submission and demonstrates the use of IBM's generative AI technologies for personalized interview preparation.

---

## ⭐ Conclusion

InterviewX demonstrates how Generative AI, RAG, and multi-agent architecture can be combined to create a personalized interview preparation platform.

By integrating **IBM Granite through IBM watsonx.ai Runtime**, the system can analyze candidate profiles, generate personalized questions, evaluate answers, identify skill gaps, and provide actionable feedback.

The project provides an end-to-end AI-powered interview training experience for students and entry-level candidates.
