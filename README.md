# DocuChat AI

> A RAG-based PDF assistant with an integrated AI-powered quiz system.  
> Upload any PDF → chat with it → quiz yourself on it.

---

## Features

- **Chat Mode** — Context-aware Q&A grounded in your document with page-level source citations
- **Quiz Mode** — Auto-generates MCQ, True/False, and Short Answer questions from document content
- **RAG Pipeline** — Semantic retrieval via FAISS ensures answers come from your document, not hallucinations
- **Performance Feedback** — Every quiz submission returns a score, per-question verdict, and AI-generated explanation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Tailwind CSS, Framer Motion, React Router |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Orchestration | LangChain |
| Vector DB | FAISS (faiss-cpu) |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenAI `gpt-4o` |
| PDF Parsing | PyMuPDF (fitz) |

---

## Project Structure

```
docuchat-ai/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py        # POST /api/upload/
│   │   │   ├── chat.py          # POST /api/chat/
│   │   │   └── quiz.py          # POST /api/quiz/generate & /submit
│   │   └── middleware/cors.py
│   ├── core/
│   │   ├── config.py            # Settings from .env
│   │   └── logger.py
│   ├── services/
│   │   ├── pdf_processor.py     # PyMuPDF text extraction
│   │   ├── chunker.py           # LangChain text splitting
│   │   ├── embeddings.py        # OpenAI embeddings
│   │   ├── vector_store.py      # FAISS save / load
│   │   ├── retriever.py         # Semantic top-K search
│   │   ├── chat_service.py      # RAG pipeline + citations
│   │   └── quiz_service.py      # Quiz generation + evaluation
│   ├── models/
│   │   ├── chat.py              # Pydantic request / response models
│   │   └── quiz.py
│   └── storage/
│       ├── uploads/             # Uploaded PDFs (gitignored)
│       └── faiss_index/         # FAISS indexes (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Router root
│   │   ├── pages/               # Home, ChatPage, QuizPage
│   │   ├── components/          # PDFUploader, ChatWindow, QuizPanel, ScoreBoard, …
│   │   ├── hooks/               # useChat, useQuiz
│   │   └── services/api.js      # Axios API layer
│   └── Dockerfile
│
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_pdf_processor.py
│   ├── test_retriever.py
│   ├── test_chat_service.py
│   └── test_quiz_service.py
│
├── notebooks/
│   ├── chunking_experiments.ipynb   # Find optimal CHUNK_SIZE & CHUNK_OVERLAP
│   └── retrieval_evals.ipynb        # Validate retrieval Hit@K quality
│
├── .env                         # API keys — never commit
├── .env.example                 # Safe template to commit
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

### 1 · Clone & configure

```bash
git clone https://github.com/your-username/docuchat-ai.git
cd docuchat-ai

cp .env.example .env
# Open .env and paste your OPENAI_API_KEY
```

---

### 2 · Run the backend

```bash
cd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt


```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3 · Run the frontend

```bash
cd frontend

npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

### 4 · Run with Docker (recommended for production)

```bash
cp .env.example .env
# Fill in OPENAI_API_KEY in .env

docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## API Reference

### Upload PDF

```
POST /api/upload/
Content-Type: multipart/form-data

file: <PDF file>
```

**Response**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "research_paper.pdf",
  "total_chunks": 47,
  "message": "PDF processed successfully."
}
```

---

### Chat

```
POST /api/chat/
Content-Type: application/json

{
  "document_id": "550e8400-...",
  "query": "What is the quiz mode?",
  "chat_history": []
}
```

**Response**
```json
{
  "answer": "Quiz Mode automatically generates MCQ, True/False, and Short Answer questions…",
  "citations": [
    { "chunk_index": 3, "page": 2, "snippet": "Quiz Mode generates questions…" }
  ]
}
```

---

### Generate Quiz

```
POST /api/quiz/generate
Content-Type: application/json

{
  "document_id": "550e8400-...",
  "question_type": "mcq",
  "num_questions": 5,
  "topic_focus": "RAG pipeline"
}
```

`question_type` options: `mcq` | `true_false` | `short_answer`

---

### Submit Quiz

```
POST /api/quiz/submit
Content-Type: application/json

{
  "quiz_id": "abc123",
  "user_answers": {
    "question-uuid-1": "B",
    "question-uuid-2": "True"
  }
}
```

**Response**
```json
{
  "quiz_id": "abc123",
  "score": 4,
  "total": 5,
  "percentage": 80.0,
  "feedback": [
    {
      "question_id": "...",
      "question": "What does RAG stand for?",
      "user_answer": "B",
      "correct_answer": "B",
      "is_correct": true,
      "feedback": "Correct! RAG stands for Retrieval-Augmented Generation."
    }
  ]
}
```

---

## Running Tests

```bash
cd tests

# All tests
pytest -v

# Single file
pytest test_chat_service.py -v

# With coverage report
pytest --cov=../backend/services --cov-report=term-missing
```

---

## Research Notebooks

Run from the `notebooks/` directory after installing backend dependencies:

```bash
cd notebooks
jupyter notebook
```

| Notebook | Purpose | Output |
|---|---|---|
| `chunking_experiments.ipynb` | Grid search chunk size × overlap | `CHUNK_SIZE`, `CHUNK_OVERLAP` for `config.py` |
| `retrieval_evals.ipynb` | Hit@K evaluation + LLM-as-Judge | `TOP_K` for `config.py` |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | **Required.** Your OpenAI secret key |
| `OPENAI_MODEL` | `gpt-4o` | LLM used for chat and quiz generation |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between consecutive chunks |
| `TOP_K` | `5` | Number of chunks retrieved per query |
| `UPLOAD_DIR` | `storage/uploads` | Directory for temporary PDF storage |
| `FAISS_INDEX_DIR` | `storage/faiss_index` | Directory for persisted FAISS indexes |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins |
| `DEBUG` | `False` | Enable FastAPI debug mode |

---

## Resume Description

> *"Developed a RAG-based PDF chatbot with an integrated AI-powered quiz system that generates context-aware questions and evaluates user responses. Implemented semantic retrieval, source-grounded answers, and interactive learning features using LangChain and FAISS."*

---

## License

MIT © DocuChat AI
