# RAG API — Retrieval-Augmented Generation over Technical Documents

A production-ready RAG pipeline built with LangChain, ChromaDB, and FastAPI.
Queries technical documents using local embeddings and a free cloud LLM via OpenRouter.

---

## Architecture

```
User Query
    │
    ▼
FastAPI  (/query)
    │
    ▼
ChromaDB  ◄──── nomic-embed-text (local, via Ollama)
    │               └── vector similarity search (k=6)
    │
    ▼
Prompt Builder
    │
    ▼
OpenRouter LLM  (nvidia/nemotron-3-super-120b-a12b — free)
    │
    ▼
JSON Response  { answer, sources }
```

**Key design choices:**
- **Embeddings run locally** via Ollama — no data sent to external APIs during indexing
- **LLM runs on OpenRouter** — access to large models without local GPU requirements
- **ChromaDB** as persistent vector store with cosine similarity search
- **FastAPI** for a clean, auto-documented REST interface

---

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Vector Store | ChromaDB |
| Embeddings | nomic-embed-text (Ollama, local) |
| LLM | nvidia/nemotron-3-super-120b-a12b (OpenRouter) |
| Orchestration | LangChain |
| Config | python-dotenv |

---

## Project Structure

```
rag-api/
├── data/                   # Place your .md documents here
│   └── your_document.md
├── chroma/                 # Auto-generated vector index (gitignored)
├── api.py                  # FastAPI application
├── create_database.py      # Document ingestion and indexing pipeline
├── query_data.py           # RAG query logic
├── requirements.txt
├── .env.example            # Environment variables template
└── .gitignore
```

---

## Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- An [OpenRouter](https://openrouter.ai) account (free)

### 1. Clone the repository

```bash
git clone https://github.com/Domenicos97/RagAPI.git
cd rag-api
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get your free API key at [openrouter.ai/keys](https://openrouter.ai/keys).

### 4. Pull the embedding model

```bash
ollama pull nomic-embed-text
```

### 5. Add your documents

Place `.md` files in the `data/` folder:

```
data/
└── your_document.md
```

### 6. Build the vector index

```bash
python create_database.py
```

Expected output:
```
Loaded 1 document(s).
Split into 24 chunks.
Saved 24 chunks to 'chroma/'.
```

### 7. Start the API

```bash
# Terminal 1 — keep Ollama running
ollama serve

# Terminal 2 — start the API
uvicorn api:app --reload --port 8000
```

---

## Usage

### Swagger UI

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API docs.

### REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status and model info |
| POST | `/query` | Query the document database |
| POST | `/rebuild-index` | Re-index documents from `data/` |
| GET | `/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual è la pressione massima del circuito?"}'
```

### Example Response

```json
{
  "answer": "La pressione massima del circuito è 320 bar.",
  "sources": ["data/your_document.md"]
}
```

---

## How It Works

1. **Ingestion** (`create_database.py`): `.md` files are loaded, split into 1000-character chunks with 200-character overlap, converted to embeddings using `nomic-embed-text`, and stored in ChromaDB.

2. **Retrieval** (`query_data.py`): the user question is embedded and compared against the vector store using cosine similarity. The top 6 most relevant chunks are retrieved.

3. **Generation**: retrieved chunks are injected into a prompt template and sent to the LLM via OpenRouter. The model generates an answer grounded exclusively in the retrieved context.

---

## Configuration

Key parameters in `create_database.py` and `query_data.py`:

| Parameter | Value | Description |
|---|---|---|
| `chunk_size` | 1000 | Characters per chunk |
| `chunk_overlap` | 200 | Overlap between chunks |
| `k` | 6 | Number of chunks retrieved per query |
| `similarity_threshold` | 0.3 | Minimum relevance score |

---
