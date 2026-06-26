# ⚖️ LegalAI – Document Assistant

An AI-powered assistant for legal-tech teams. Upload PDF or DOCX contracts and agreements, then ask questions in natural language. Powered by Claude (Anthropic) with RAG (Retrieval-Augmented Generation) and streaming responses.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 📄 File Support | PDF and DOCX |
| 🤖 AI Engine | Claude claude-sonnet-4-6 via Anthropic API |
| 🔍 RAG Pipeline | FAISS vector store + Voyage Law embeddings |
| ⚡ Streaming | Server-Sent Events for real-time answers |
| 💬 Conversation History | Full multi-turn Q&A per session |
| 🐳 Docker | One-command deployment |

---

## 🏗️ Architecture

```
legal-ai-assistant/
├── backend/
│   └── app/
│       ├── api/          # FastAPI routes
│       ├── core/         # Config, exceptions
│       ├── models/       # Pydantic schemas
│       └── services/
│           ├── document_parser.py   # Strategy: PDF / DOCX parsers
│           ├── vector_store.py      # FAISS embedding store
│           ├── session_manager.py   # Conversation history
│           ├── llm_service.py       # Claude API (stream + sync)
│           └── document_qa.py       # Facade orchestrator
├── frontend/
│   └── src/
│       ├── components/   # React UI components
│       └── services/     # API client
└── docker-compose.yml
```

### Design Patterns Used
- **Strategy** — `DocumentParser` (PDF vs DOCX interchangeable)
- **Factory** — `DocumentParserFactory` (selects parser by extension)
- **Facade** — `DocumentQAService` (single interface over all services)
- **Singleton** — `Settings` via `@lru_cache`, service instances via DI

---

## 🚀 Local Setup (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

### 1 — Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env .env
# Open .env and set ANTHROPIC_API_KEY=sk-ant-...

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend available at: http://localhost:8000
Swagger UI at: http://localhost:8000/docs

### 2 — Frontend

```bash
cd frontend
npm install
npm start
```

Frontend available at: http://localhost:3000

---

## 🐳 Docker Setup

```bash
# 1. Add your API key
cp backend/.env backend/.env
# Edit backend/.env → set ANTHROPIC_API_KEY

# 2. Build and run
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
<img width="1920" height="1018" alt="image" src="https://github.com/user-attachments/assets/f1ff20aa-3ffa-43c6-b653-3254ace277a5" />

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/upload` | Upload PDF or DOCX → returns `session_id` |
| POST | `/api/v1/query` | Ask a question (full response) |
| POST | `/api/v1/query/stream` | Ask a question (streaming SSE) |
| GET | `/api/v1/session/{id}` | Get session info |
| DELETE | `/api/v1/session/{id}` | Delete session |
| GET | `/api/v1/sessions` | List all sessions |
| GET | `/health` | Health check |

---

## 💬 Sample Queries & Outputs

### Query 1 — Termination Clauses
**Input:** "What are the termination clauses in this agreement?"
<img width="1815" height="865" alt="image" src="https://github.com/user-attachments/assets/7e77f657-a918-4793-8098-4d08a77e040a" />

**Output:**
> According to Section 12 of the agreement, either party may terminate this contract with **30 days written notice**. Immediate termination is permitted in cases of material breach that remains uncured for 15 days after written notice, or upon insolvency of either party.

---

### Query 2 — Key Obligations
**Input:** "Summarize the key obligations of each party."
<img width="1742" height="900" alt="image" src="https://github.com/user-attachments/assets/2f762147-d3a7-491e-9ef7-fef61c17902c" />


**Output:**
> **Client Obligations:**
> - Pay invoices within 30 days of receipt
> - Provide timely access to necessary resources
> - Assign a designated project coordinator
>
> **Vendor Obligations:**
> - Deliver services per the Statement of Work
> - Maintain confidentiality of all client data
> - Carry minimum $1M professional liability insurance

---

### Query 3 — Governing Law (follow-up)
**Input:** "Which state's law governs this contract?"

**Output:**
> The agreement is governed by the laws of the **State of Delaware**, as stated in Section 18.2. Any disputes must be resolved through binding arbitration in Wilmington, Delaware.

---

### Query 4 — Penalty Clauses
**Input:** "Are there any late payment penalties?"

<img width="1742" height="878" alt="image" src="https://github.com/user-attachments/assets/e44fca35-8122-496a-86ec-12e7260a17e7" />



**Output:**
> Yes. Section 7.3 specifies that invoices unpaid after 30 days accrue interest at **1.5% per month** (18% annually). The vendor may also suspend services after 45 days of non-payment with 5 days written notice.

---

## ⚙️ Configuration

Edit `backend/.env` to adjust behavior:

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key |
| `MAX_FILE_SIZE_MB` | `50` | Max upload size |
| `CHUNK_SIZE` | `1000` | Text chunk size for RAG |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_K` | `5` | Number of chunks retrieved per query |
| `MAX_TOKENS` | `2048` | Max tokens in LLM response |

---

## 🛠️ Tech Stack

**Backend:** FastAPI · LangChain · Anthropic SDK · FAISS · pypdf · python-docx

**Frontend:** React 18 · react-dropzone · react-markdown · Axios

**Infrastructure:** Docker · Nginx · Uvicorn
