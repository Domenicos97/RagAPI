import os
import shutil
import glob
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()
    if not documents:
        return
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_documents():
    documents = []
    files = glob.glob(os.path.join(DATA_PATH, "*.md"))

    if not files:
        print(f"No .md files found in {DATA_PATH}/")
        return []

    for file_path in files:
        loader = TextLoader(file_path, encoding="utf-8")
        documents.extend(loader.load())

    print(f"Loaded {len(documents)} document(s).")
    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=CHROMA_PATH
    )

    print(f"Saved {len(chunks)} chunks to '{CHROMA_PATH}/'.")

if __name__ == "__main__":
    main()
