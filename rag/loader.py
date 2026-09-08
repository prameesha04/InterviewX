"""
RAG knowledge base loader.
Reads all .txt files from the knowledge_base/ directory,
chunks them, embeds them using a sentence-transformer model,
and persists them to a ChromaDB vector store.
"""

import os
import glob
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "interviewx_kb"


def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vector_store(force_rebuild: bool = False) -> Chroma:
    """
    Load all knowledge base documents, chunk them, embed, and persist to ChromaDB.
    If the store already exists, skip rebuilding unless force_rebuild=True.
    """
    persist_dir = os.path.abspath(CHROMA_PERSIST_DIR)

    embeddings = _get_embeddings()

    # If store already exists, just load it
    if os.path.exists(persist_dir) and not force_rebuild:
        print(f"[RAG] Loading existing vector store from {persist_dir}")
        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )

    print("[RAG] Building vector store from knowledge base...")

    kb_dir = os.path.abspath(KNOWLEDGE_BASE_DIR)
    txt_files = glob.glob(os.path.join(kb_dir, "*.txt"))

    if not txt_files:
        raise FileNotFoundError(
            f"No .txt files found in knowledge_base directory: {kb_dir}"
        )

    documents = []
    for filepath in txt_files:
        loader = TextLoader(filepath, encoding="utf-8")
        docs = loader.load()
        # Tag each document with its source file for metadata
        for doc in docs:
            doc.metadata["source"] = os.path.basename(filepath)
        documents.extend(docs)
        print(f"[RAG] Loaded: {os.path.basename(filepath)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"[RAG] Created {len(chunks)} chunks from {len(documents)} documents")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_dir,
    )
    print(f"[RAG] Vector store persisted to {persist_dir}")
    return vector_store


def get_vector_store() -> Chroma:
    """Return the vector store, building it if necessary."""
    return build_vector_store()
