import argparse
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

CHROMA_PATH = "chroma"
LLM_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

PROMPT_TEMPLATE = """
You are a technical assistant. Answer the question based exclusively on the
following context extracted from the technical manual.
If the value or information is present in the context, report it precisely.

Context:
{context}

---

Question: {question}

Answer:
"""

def get_llm():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not set.\n"
            "Copy .env.example to .env and fill in your key."
        )
    return ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0,
    )

def query(query_text: str) -> dict:
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_relevance_scores(query_text, k=6)

    if len(results) == 0 or results[0][1] < 0.3:
        return {
            "risposta": "No relevant results found in the document.",
            "fonti": []
        }

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = get_llm()
    response = model.invoke(prompt)

    sources = list(set([doc.metadata.get("source", None) for doc, _score in results]))

    return {
        "risposta": response.content,
        "fonti": sources
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="Question to ask the database.")
    args = parser.parse_args()

    result = query(args.query_text)
    print(f"\n[ANSWER]:\n{result['risposta']}")
    print(f"\n[SOURCES]: {result['fonti']}")

if __name__ == "__main__":
    main()
