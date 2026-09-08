# InterviewX – AI-Powered Personalized Interview Trainer

InterviewX is an AI-powered personalized interview preparation platform designed for students and entry-level candidates.

It analyzes a candidate's profile, generates personalized technical, behavioral, and HR interview questions using RAG, and evaluates candidate answers using IBM Granite through IBM watsonx.ai Runtime.

---

## 🎯 Project Objective

InterviewX provides an end-to-end AI-powered interview training experience:

Candidate Profile
→ Profile Analysis
→ Personalized Question Generation
→ Candidate Answer
→ AI Evaluation
→ Feedback & Recommendations

The system uses multiple specialized AI agents to provide personalized interview preparation.

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   Candidate Profile │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Profile Analysis    │
                    │ Agent               │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ RAG Knowledge Base  │
                    │     ChromaDB        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Question Generation │
                    │ Agent               │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Candidate Answer    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evaluation Agent    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Feedback Dashboard  │
                    └─────────────────────┘
