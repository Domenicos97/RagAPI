from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query_data import query
from create_database import generate_data_store

app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API over technical documents.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str | None]

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "RAG API is running",
        "model": "nvidia/nemotron-super-120b-v1:free",
        "embeddings": "nomic-embed-text (local via Ollama)"
    }

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """Query the vector database with a natural language question."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        result = query(request.question)
        return QueryResponse(answer=result["risposta"], sources=result["fonti"])
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/rebuild-index")
def rebuild_index():
    """Rebuild the Chroma vector index from documents in data/."""
    try:
        generate_data_store()
        return {"status": "ok", "message": "Index rebuilt successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding index: {str(e)}")

@app.get("/health")
def health():
    return {"status": "healthy"}
