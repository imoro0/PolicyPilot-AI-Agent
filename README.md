# PolicyPilot AI Agent

An AI-powered policy assistant built with **Python, FastAPI, LangGraph, Gemini, and Retrieval-Augmented Generation (RAG)**. PolicyPilot answers questions using information retrieved from policy documents.

## Features

- **Policy Q&A:** Ask questions about available Airbnb policy documents.
- **RAG Pipeline:** Retrieves relevant policy text from a ChromaDB vector database.
- **Gemini Integration:** Uses Google's Gemini Flash-Lite model to generate answers.
- **Agentic Workflow:** Uses LangGraph to route policy questions and handle supported workflows.
- **Conversation Memory:** Maintains recent conversation history by session.
- **Policy Tools:** Includes policy search, eligibility checks, and simulated action requests.
- **Web Interface:** Simple frontend built with HTML, CSS, and JavaScript.
- **LangSmith Tracing:** Supports tracing and monitoring of agent runs.

## Tech Stack

- Python
- FastAPI
- LangGraph
- Google Gemini API (`google-genai`)
- ChromaDB
- Hugging Face sentence-transformer embeddings
- HTML, CSS, JavaScript
- LangSmith

## Project Structure

```text
PolicyPilot-AI-Agent/
├── Backend/
│   ├── Agent/
│   ├── API/
│   ├── LLM/
│   ├── Memory/
│   ├── RAG/
│   ├── Schemas/
│   ├── Services/
│   ├── Tools/
│   ├── VectorDB/
│   └── main.py
├── Frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── Data/
│   ├── Policies/
│   ├── Uploads/
│   └── ChromaDB/
├── Tests/
├── Docs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.12 recommended
- Git
- A Google Gemini API key
- Internet access for API requests and initial model downloads

## Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd PolicyPilot-AI-Agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your own Gemini API key.

Never commit your real `.env` file or API keys to GitHub.

### 5. Prepare the policy data

Place authorized policy PDF documents in `Data/Policies/`. Initialize